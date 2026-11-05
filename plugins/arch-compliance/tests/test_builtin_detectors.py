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
