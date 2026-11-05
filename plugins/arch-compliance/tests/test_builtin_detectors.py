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
