"""Both silent substitution failures become loud."""
from __future__ import annotations

import pytest

from acf.exceptions import TemplateRenderError
from acf.template import render_template


def test_fills_every_token():
    out = render_template("a {{ONE}} b {{TWO}}", {"ONE": "1", "TWO": "2"})
    assert out == "a 1 b 2"


def test_repeated_token_is_filled_everywhere():
    out = render_template("{{X}} and {{X}}", {"X": "v"})
    assert out == "v and v"


def test_unfilled_token_is_refused():
    """Review Focus 4a: a token the mapping cannot fill.

    str.replace leaves the literal token in the output and says nothing, so a
    renamed placeholder ships '{{ARCHITECTURE_EXCERPT}}' to a subagent.
    """
    with pytest.raises(TemplateRenderError) as excinfo:
        render_template("a {{ONE}} b {{TWO}}", {"ONE": "1"})
    assert "TWO" in str(excinfo.value)


def test_unused_mapping_key_is_refused():
    """Review Focus 4b: a mapping key the text never uses."""
    with pytest.raises(TemplateRenderError) as excinfo:
        render_template("a {{ONE}}", {"ONE": "1", "STALE": "x"})
    assert "STALE" in str(excinfo.value)


def test_single_braces_are_left_alone():
    """The judge prompt carries a literal JSON example."""
    text = 'respond with {"violation": bool} and {{DIFF}}'
    out = render_template(text, {"DIFF": "d"})
    assert out == 'respond with {"violation": bool} and d'


def test_value_containing_a_token_is_not_rescanned():
    """A substituted value is data, not template."""
    out = render_template("{{A}}", {"A": "{{B}}"})
    assert out == "{{B}}"


JUDGE_PROMPT_EXPECTED = (
    "You are an architecture compliance judge.\n"
    "Mandate id: M1\n"
    "Title: A title\n"
    "Severity: BLOCK\n"
    "Detector/prompt id: d1\n"
    "Architecture anchor: An Anchor\n"
    "\n"
    "Review the unified diff. Respond with JSON only:\n"
    '{"violation": bool, "severity": "BLOCK"|"WARN", "confidence": '
    '"high"|"medium"|"low", "message": string, "path": string|null, '
    '"line": int|null}\n'
    "Set violation=false when the diff does not violate the mandate.\n"
    "\n"
    "DIFF:\n"
    "DIFF_BODY\n"
)


def _sample_mandate():
    from acf.registry import Mandate

    return Mandate(
        id="M1",
        title="A title",
        severity="BLOCK",
        detection="llm",
        detector="d1",
        languages="python",
        call_sites=[],
        exemption_tokens=[],
        status="enforced",
        arch_anchor="An Anchor",
    )


def test_judge_prompt_is_byte_identical_across_the_migration():
    """Characterization guard: this passed BEFORE the template migration and
    must pass after. Moving the skeleton into a file must not alter one byte of
    what the judge sends to the model.
    """
    from acf.judge import _build_prompt

    out = _build_prompt(diff_text="DIFF_BODY", mandate=_sample_mandate())
    assert out == JUDGE_PROMPT_EXPECTED


def test_judge_prompt_carries_every_field_the_builder_supplies():
    """The template and _build_prompt's mapping must agree, or render refuses."""
    from acf.judge import _build_prompt

    out = _build_prompt(diff_text="DIFF_BODY", mandate=_sample_mandate())
    for expected in ("M1", "A title", "BLOCK", "d1", "An Anchor", "DIFF_BODY"):
        assert expected in out
    assert "{{" not in out
    assert '"violation": bool' in out
