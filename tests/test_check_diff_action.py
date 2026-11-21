"""Structural pins on the check-diff composite action (its behaviour is proven by the CI `action` job)."""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ACTION = ROOT / ".github/actions/check-diff/action.yml"


def _action() -> dict:
    return yaml.safe_load(ACTION.read_text(encoding="utf-8"))


def test_composite_with_pinned_inputs():
    a = _action()
    assert a["runs"]["using"] == "composite"
    assert {k: v.get("default") for k, v in a["inputs"].items()} == {
        "base": "", "repo": ".", "trusted-checkout": "true",
        "python-version": "3.12", "node-version": "22", "host-setup": ""}


def test_step_order_and_guards():
    text = ACTION.read_text(encoding="utf-8")
    first = _action()["runs"]["steps"][0]["run"]
    assert "pyproject.toml" in first
    assert "plugins/arch-compliance/detectors/typescript/package.json" in first
    assert "runner.os == 'Windows'" in text
    assert "--is-shallow-repository" in text and "fetch-depth: 0" in text
    assert "github.event.repository.default_branch" in text
    assert "set -o pipefail" in text and "acf-check-diff.txt" in text
    assert "--call-site ci" in text


def test_trusted_checkout_only_when_true():
    text = ACTION.read_text(encoding="utf-8")
    assert "trusted-checkout must be true or false" in text
