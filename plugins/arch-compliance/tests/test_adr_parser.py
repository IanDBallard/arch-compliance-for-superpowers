"""Strict single-JSON-block parsing for reviewer payloads (§3, Architectural Contract 5)."""
import json

import pytest

from acf.adr.contract import RefuterPayload, SweeperPayload
from acf.adr.parser import parse_reviewer_payload
from acf.exceptions import ReviewerContractViolationError

_REFUTER_BODY = {
    "reviewer": "refuter",
    "claim_verdicts": [
        {"id": "C1", "verdict": "REFUTED", "evidence": "scripts/core/x.py:12",
         "reasoning": "absent"},
    ],
    "unanchored_findings": [],
    "looked_for_but_did_not_find": ["a seq*10 block under scripts/"],
}


def _fence(body: dict) -> str:
    return "Here is my adjudication.\n\n```json\n" + json.dumps(body, indent=2) + "\n```\n"


def test_parses_a_well_formed_refuter_payload():
    result = parse_reviewer_payload(_fence(_REFUTER_BODY), "refuter")
    assert isinstance(result, RefuterPayload)
    assert result.claim_verdicts[0].verdict == "REFUTED"


def test_parses_a_sweeper_payload_into_the_sweeper_class():
    body = {
        "reviewer": "sweeper",
        "claim_verdicts": [],
        "unanchored_findings": [],
        "looked_for_but_did_not_find": ["a second book_order assigner"],
        "relationships": [],
        "two_owner_counts": {},
        "document_conflicts": [],
    }
    result = parse_reviewer_payload(_fence(body), "sweeper")
    assert isinstance(result, SweeperPayload)


def test_no_json_block_is_a_violation():
    with pytest.raises(ReviewerContractViolationError, match="no ```json fenced block"):
        parse_reviewer_payload("I could not find anything wrong.", "refuter")


def test_two_json_blocks_is_a_violation():
    doubled = _fence(_REFUTER_BODY) + _fence(_REFUTER_BODY)
    with pytest.raises(ReviewerContractViolationError, match="multiple \\(2\\)"):
        parse_reviewer_payload(doubled, "refuter")


def test_non_json_body_is_a_violation():
    with pytest.raises(ReviewerContractViolationError, match="JSON parse failed"):
        parse_reviewer_payload("```json\n{not json,}\n```", "refuter")


def test_schema_mismatch_is_a_violation_with_a_key_diff():
    body = dict(_REFUTER_BODY)
    del body["looked_for_but_did_not_find"]
    with pytest.raises(ReviewerContractViolationError) as exc:
        parse_reviewer_payload(_fence(body), "refuter")
    message = str(exc.value)
    assert "schema validation" in message
    # The diff block itself, not just Pydantic's own "Field required" text (which
    # already contains the field name and would pass even if the diff were
    # broken, empty, or deleted): the "Key diff:" header must be present, and a
    # removed-line entry naming the missing key.
    assert "Key diff:" in message
    assert "-looked_for_but_did_not_find" in message


def test_backslash_path_is_a_violation_with_the_posix_hint():
    body = json.loads(json.dumps(_REFUTER_BODY))
    body["claim_verdicts"][0]["evidence"] = r"scripts\core\x.py:12"
    with pytest.raises(ReviewerContractViolationError) as exc:
        parse_reviewer_payload(_fence(body), "refuter")
    # Pydantic's own ValueError text ("must be POSIX (no backslashes): ...")
    # already contains "POSIX", so asserting only that substring would pass
    # even if the parser's own hint-append branch were deleted. Assert the
    # literal hint text the PARSER adds, so this test is evidence about the
    # parser's branch, not about contract.py's message.
    assert "Hint: every path field must be POSIX (no backslashes)" in str(exc.value)


def test_regex_backslash_in_evidence_parses():
    # 2026-10-08: two refuter dispatches quoted a grep regex as evidence and the
    # run aborted. Quoted search text is not a path and must parse.
    body = json.loads(json.dumps(_REFUTER_BODY))
    body["claim_verdicts"][0]["evidence"] = r"grep 'os\.utime' -> scripts/core/x.py:12"
    payload = parse_reviewer_payload(_fence(body), "refuter")
    assert payload.claim_verdicts[0].evidence.startswith("grep 'os\\.utime'")


def test_extra_key_is_a_violation():
    # Architectural Contract 5: "matching its schema ... no partial acceptance."
    # A plausible fabrication (a reviewer inventing a confidence score it was
    # never asked for), not an arbitrary nonsense key, so this reads as the
    # real failure mode _StrictModel's extra="forbid" exists to catch.
    body = dict(_REFUTER_BODY, confidence=0.9)
    with pytest.raises(ReviewerContractViolationError) as exc:
        parse_reviewer_payload(_fence(body), "refuter")
    message = str(exc.value)
    assert "schema validation" in message
    assert "confidence" in message


def test_non_object_json_is_a_violation():
    # A bare JSON list parses fine (no JSONDecodeError) but is not a dict, so
    # the reviewer-identity check and the `data.keys()` key-diff lookup must
    # both tolerate it rather than crashing with AttributeError.
    with pytest.raises(ReviewerContractViolationError, match="schema validation"):
        parse_reviewer_payload("```json\n[1, 2, 3]\n```", "refuter")


def test_silence_without_coverage_is_a_violation():
    body = dict(_REFUTER_BODY, unanchored_findings=[], looked_for_but_did_not_find=[])
    with pytest.raises(ReviewerContractViolationError, match="silence is not coverage"):
        parse_reviewer_payload(_fence(body), "refuter")


def test_wrong_reviewer_identity_is_a_violation():
    with pytest.raises(ReviewerContractViolationError, match="dispatched as 'sweeper'"):
        parse_reviewer_payload(_fence(_REFUTER_BODY), "sweeper")


def test_violation_message_includes_a_payload_excerpt_for_diagnosis():
    with pytest.raises(ReviewerContractViolationError) as exc:
        parse_reviewer_payload("nothing fenced here at all", "refuter")
    assert "nothing fenced here at all" in str(exc.value)
