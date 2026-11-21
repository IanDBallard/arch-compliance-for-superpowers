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


# --- Behaviour of the "Resolve inputs" and gate steps, run under bash with a stub gate ---

import os  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402

import pytest  # noqa: E402

BASH = shutil.which("bash")


def _step(name_prefix: str) -> str:
    [step] = [s for s in _action()["runs"]["steps"] if s.get("name", "").startswith(name_prefix)]
    return step["run"]


def _resolve_then_gate(tmp_path, *, trusted="true", repo=".", base="", base_ref="", default_branch="main"):
    """Run the action's Resolve and gate scripts as GitHub would, with a stub acf-check-diff."""
    venv_bin = tmp_path / "acf-venv" / "bin"
    venv_bin.mkdir(parents=True)
    stub = venv_bin / "acf-check-diff"
    stub.write_text('#!/usr/bin/env bash\nprintf "%s\n" "$@"\n', encoding="utf-8", newline="\n")
    stub.chmod(0o755)
    gh_env = tmp_path / "github_env"
    gh_env.write_text("", encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if not k.startswith(("ACF_", "GITHUB_"))}
    env.update(RUNNER_TEMP=str(tmp_path), GITHUB_ENV=str(gh_env), GITHUB_WORKSPACE="/ws",
               GITHUB_BASE_REF=base_ref, IN_TRUSTED=trusted, IN_REPO=repo, IN_BASE=base,
               DEFAULT_BRANCH=default_branch)
    r = subprocess.run([BASH, "--noprofile", "--norc", "-eo", "pipefail", "-c", _step("Resolve inputs")],
                       env=env, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        return r, None
    for line in gh_env.read_text(encoding="utf-8").splitlines():
        key, _, value = line.partition("=")
        env[key] = value
    g = subprocess.run([BASH, "--noprofile", "--norc", "-eo", "pipefail", "-c",
                        _step("Architecture compliance")],
                       env=env, capture_output=True, text=True, encoding="utf-8")
    return r, g


@pytest.mark.skipif(BASH is None, reason="needs bash")
def test_trusted_true_passes_flag(tmp_path):
    _, g = _resolve_then_gate(tmp_path, trusted="true")
    assert g.returncode == 0, g.stderr
    assert "--trusted-checkout" in g.stdout.split()


@pytest.mark.skipif(BASH is None, reason="needs bash")
def test_trusted_false_omits_flag(tmp_path):
    _, g = _resolve_then_gate(tmp_path, trusted="false")
    assert g.returncode == 0, g.stderr
    assert "--trusted-checkout" not in g.stdout.split()
    assert "ci" in g.stdout.split()


@pytest.mark.skipif(BASH is None, reason="needs bash")
def test_trusted_other_value_refused(tmp_path):
    r, g = _resolve_then_gate(tmp_path, trusted="yes")
    assert r.returncode == 1 and g is None
    assert "trusted-checkout must be true or false, got 'yes'" in r.stdout


@pytest.mark.skipif(BASH is None, reason="needs bash")
@pytest.mark.parametrize("base,base_ref,expected", [
    ("", "release", "origin/release"),   # pull_request: the PR's base
    ("", "", "origin/main"),             # push: the default branch
    ("main", "release", "main"),         # explicit input wins
])
def test_base_derivation(tmp_path, base, base_ref, expected):
    _, g = _resolve_then_gate(tmp_path, base=base, base_ref=base_ref)
    args = g.stdout.split()
    assert args[args.index("--base") + 1] == expected


@pytest.mark.skipif(BASH is None, reason="needs bash")
def test_repo_relative_and_absolute(tmp_path):
    _, g = _resolve_then_gate(tmp_path, repo="sub/dir")
    args = g.stdout.split()
    assert args[args.index("--repo") + 1] == "/ws/sub/dir"
    _, g = _resolve_then_gate(tmp_path / "b", repo="/abs/host")
    args = g.stdout.split()
    assert args[args.index("--repo") + 1] == "/abs/host"
