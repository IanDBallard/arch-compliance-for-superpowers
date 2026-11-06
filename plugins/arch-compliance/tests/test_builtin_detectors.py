from acf.detectors import KNOWN_DETECTORS
from acf.judge import LLM_PROMPT_IDS
from acf.registry import DIFF_CALL_SITES, TIER1_CALL_SITES
from acf.detectors.build_artifacts import build_artifact_args
from acf.detectors.facade_sinks import facade_sink_args
from acf.detectors.fsm_guard import fsm_guard_args


def test_args_defaults():
    assert facade_sink_args({}) == {"target_literal_re": ""}
    assert fsm_guard_args({}) == {"state_field": "", "validator_name": ""}
    assert build_artifact_args({}) == {} and build_artifact_args({"path_prefixes": []}) == {}


def test_args_pass_through():
    assert facade_sink_args(
        {"target_literal_re": "x", "allowlist_globs": None, "atomic_is_sink": False}
    ) == {"target_literal_re": "x", "allowlist_globs": None, "atomic_is_sink": False}
    assert build_artifact_args({"path_prefixes": ["dist/"]}) == {"path_prefixes": ["dist/"]}


def test_ratchet_uses_pack_predicate():
    import acf.detectors.fail_loud_ratchet as r
    import acf.detectors.python_pack as p

    assert r.is_bare_or_exception is p.is_bare_or_exception


def test_no_llm_prompt_id_is_a_known_detector():
    assert not (set(KNOWN_DETECTORS) & LLM_PROMPT_IDS)


def test_ratchet_runs_at_diff_sites_and_every_other_detector_at_tier1():
    assert KNOWN_DETECTORS["fail_loud_ratchet"].call_sites == DIFF_CALL_SITES
    for key, contract in KNOWN_DETECTORS.items():
        if key != "fail_loud_ratchet":
            assert contract.call_sites == TIER1_CALL_SITES, key


def test_ts_pack_emits_no_mandate_id_and_rule_files_spell_each_detector():
    from pathlib import Path

    from acf.detectors.typescript_bridge import TS_MANDATE_IDS

    src = Path(__file__).resolve().parents[1] / "detectors" / "typescript" / "src"
    texts = {p: p.read_text(encoding="utf-8") for p in src.rglob("*.ts")}
    assert texts
    assert not [p for p, t in texts.items() if "mandate_id" in t]
    rules = "\n".join(t for p, t in texts.items() if p.parent.name == "rules")
    for key in TS_MANDATE_IDS:
        assert f'detector: "{key}"' in rules, key


# ------------------------------------------------- contract against dispatch

import json as _json
import shutil as _shutil
import subprocess as _subprocess
import sys as _sys
from pathlib import Path as _Path

import pytest as _pytest

from acf.detectors.build_artifacts import BUILD_ARTIFACT_DETECTOR_ID
from acf.detectors.facade_sinks import FACADE_SINK_DETECTOR_ID
from acf.detectors.fail_loud_ratchet import FAIL_LOUD_RATCHET_DETECTOR_ID
from acf.detectors.fsm_guard import FSM_GUARD_DETECTOR_ID
from acf.detectors.typescript_bridge import _PACK_ROOT, TS_MANDATE_IDS
from acf.registry import HOOK_CALL_SITES

_GATE = _Path(__file__).resolve().parents[1] / "hooks" / "posttooluse_gate.py"

_PY_TRIGGERS = """import json


def f(o, path):
    try:
        g()
    except Exception:
        pass
    if hasattr(o, "x"):
        pass
    json.dumps({"p": str(path)})
    open("facade.yml", "w")
    o.state = 1
"""

_TS_TRIGGERS = """export function f(): void {
  try {
    g();
  } catch (e) {}
}
export const x: any = 1;
"""

_GUARDS = {BUILD_ARTIFACT_DETECTOR_ID, FAIL_LOUD_RATCHET_DETECTOR_ID}
_PARAMS = {
    FACADE_SINK_DETECTOR_ID: {"target_literal_re": "facade\\.yml"},
    FSM_GUARD_DETECTOR_ID: {"state_field": "state", "validator_name": "validate_transition"},
    BUILD_ARTIFACT_DETECTOR_ID: {"path_prefixes": ["dist/"]},
    FAIL_LOUD_RATCHET_DETECTOR_ID: {"baseline": "config/architecture/fail_loud_ratchet.json"},
}


def _node_available() -> bool:
    return (_PACK_ROOT / "node_modules").is_dir() and _shutil.which("npx") is not None


def _row(detector: str, sites: frozenset[str]) -> str:
    contract = KNOWN_DETECTORS[detector]
    detection = "guard" if detector in _GUARDS else "ast"
    if detector in TS_MANDATE_IDS:
        languages = "typescript"
    elif detector == BUILD_ARTIFACT_DETECTOR_ID:
        languages = "both"
    else:
        languages = "python"
    text = (
        f"- id: {contract.mandate_id}\n"
        f"  title: {detector}\n"
        "  severity: BLOCK\n"
        f"  detection: {detection}\n"
        f"  detector: {detector}\n"
        f"  languages: {languages}\n"
        f"  call_sites: [{', '.join(sorted(sites))}]\n"
        "  exemption_tokens: []\n"
        "  status: enforced\n"
        '  arch_anchor: "# Contract"\n'
    )
    params = _PARAMS.get(detector)
    if params:
        text += "  params:\n" + "".join(
            f"    {k}: {_json.dumps(v)}\n" for k, v in params.items()
        )
    return text


def _git(repo: _Path, *args: str) -> None:
    _subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def _fixture_repo(tmp_path: _Path, sites: frozenset[str], *, with_ts: bool) -> tuple[_Path, list[str], set[str]]:
    repo = tmp_path / "repo"
    (repo / "config" / "architecture").mkdir(parents=True)
    (repo / "src").mkdir()
    (repo / "dist").mkdir()
    detectors = [
        d
        for d, c in KNOWN_DETECTORS.items()
        if sites & c.call_sites and (with_ts or d not in TS_MANDATE_IDS)
    ]
    (repo / "config" / "architecture" / "mandates.yml").write_text(
        "\n".join(_row(d, sites) for d in detectors), encoding="utf-8"
    )
    (repo / "config" / "architecture" / "fail_loud_ratchet.json").write_text(
        '{"files": {}}\n', encoding="utf-8"
    )
    edited = ["src/py_bad.py", "dist/out.txt"]
    (repo / "src" / "py_bad.py").write_text(_PY_TRIGGERS, encoding="utf-8")
    (repo / "dist" / "out.txt").write_text("built\n", encoding="utf-8")
    if with_ts:
        (repo / "src" / "ts_bad.ts").write_text(_TS_TRIGGERS, encoding="utf-8")
        edited.append("src/ts_bad.ts")
    expected = {KNOWN_DETECTORS[d].mandate_id for d in detectors}
    return repo, edited, expected


@_pytest.mark.parametrize("gate", ["ci", "precommit", "hook"])
def test_contract_against_dispatch(tmp_path, capsys, gate):
    """Each gate reports exactly the built-ins KNOWN_DETECTORS says run there."""
    with_ts = _node_available()
    sites = HOOK_CALL_SITES if gate == "hook" else frozenset({gate})
    repo, edited, expected = _fixture_repo(tmp_path, sites, with_ts=with_ts)
    if gate == "hook":
        (repo / ".acf").mkdir()
        (repo / ".acf" / "enabled").write_text("", encoding="utf-8")
        proc = _subprocess.run(
            [_sys.executable, str(_GATE), "--repo", str(repo), "--format", "json",
             *[str(repo / p) for p in edited]],
            cwd=repo, capture_output=True, text=True, input="", check=False,
        )
        assert proc.returncode == 1, proc.stderr
        findings = _json.loads(proc.stdout)
    else:
        from acf.cli_check_diff import main

        _git(repo, "init")
        _git(repo, "add", *edited)
        code = main(["--mode", "staged", "--repo", str(repo), "--call-site", gate, "--json"])
        assert code == 1, capsys.readouterr().err
        findings = _json.loads(capsys.readouterr().out)
    observed = {f["mandate_id"] for f in findings}
    assert observed == expected
    if not with_ts:
        _pytest.skip(
            f"gate {gate}: TypeScript ids {sorted(TS_MANDATE_IDS.values())} not checked "
            "(Node pack or npx unavailable); every other id was"
        )


def _readme_detector_rows():
    from pathlib import Path

    readme = Path(__file__).resolve().parents[3] / "README.md"
    lines = readme.read_text(encoding="utf-8").splitlines()
    start = next(
        (
            i for i, line in enumerate(lines)
            if line.startswith("|")
            and [c.strip() for c in line.strip().strip("|").split("|")][:2]
            == ["Detector id", "Mandate id"]
        ),
        None,
    )
    assert start is not None, "README.md has no detector table with a 'Detector id | Mandate id' header"
    header = [c.strip() for c in lines[start].strip().strip("|").split("|")]
    assert "Call sites" in header, header
    rows = []
    for line in lines[start + 2:]:
        if not line.startswith("|"):
            break
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        rows.append(dict(zip(header, cells, strict=True)))
    return rows


def _ticks(cell):
    import re

    return re.findall(r"`([^`]+)`", cell)


def test_readme_detector_table_matches_known_detectors():
    rows = _readme_detector_rows()
    assert rows
    seen = set()
    for row in rows:
        (detector_id,) = _ticks(row["Detector id"])
        (mandate_id,) = _ticks(row["Mandate id"])
        assert detector_id in KNOWN_DETECTORS, detector_id
        contract = KNOWN_DETECTORS[detector_id]
        assert mandate_id == contract.mandate_id, detector_id
        assert set(_ticks(row["Call sites"])) == set(contract.call_sites), detector_id
        seen.add(detector_id)
    from acf.detectors.typescript_bridge import TS_MANDATE_IDS

    python_keys = set(KNOWN_DETECTORS) - set(TS_MANDATE_IDS)
    assert python_keys <= seen, sorted(python_keys - seen)
