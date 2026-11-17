import pytest

from acf.agent_payload import extract_json_block
from acf.exceptions import AuditorContractViolationError, ReviewerContractViolationError


@pytest.mark.parametrize("err", [AuditorContractViolationError, ReviewerContractViolationError])
def test_zero_blocks_raise_passed_class(err):
    with pytest.raises(err, match="g1 payload contains no ```json fenced block"):
        extract_json_block("no fence", subject="g1", error=err)


def test_two_blocks_raise():
    two = "```json\n{}\n```\n```json\n{}\n```"
    with pytest.raises(AuditorContractViolationError, match=r"multiple \(2\)"):
        extract_json_block(two, subject="g1", error=AuditorContractViolationError)


def test_bad_json_raises():
    with pytest.raises(AuditorContractViolationError, match="g1 JSON parse failed"):
        extract_json_block(
            "```json\n{nope\n```", subject="g1", error=AuditorContractViolationError
        )


def test_returns_decoded():
    assert extract_json_block(
        '```json\n{"a": 1}\n```', subject="g", error=AuditorContractViolationError
    ) == {"a": 1}
