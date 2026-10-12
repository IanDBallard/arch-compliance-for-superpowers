"""The citation classifier must not read "git could not answer" as "no".

``_existed_ever`` asks git whether a path was ever committed. On a shallow clone
(every cloud session; any ``--depth`` CI checkout) the commit that deleted a file
is outside the clone, so git answers with nothing — and a correct historical
citation used to classify ``unresolved`` and hard-fail the review gate. The same
module read every failing git command as a negative answer. Both now raise
``CitationHistoryUnavailableError`` (plan PLAN_CI_TEST_HYGIENE, item 2).
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from acf.adr.citations import _existed_ever, _is_ignored, classify_citation
from acf.exceptions import CitationHistoryUnavailableError

_GIT_ID = ["-c", "user.email=ci@example.invalid", "-c", "user.name=ci", "-c", "commit.gpgsign=false"]


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *_GIT_ID, *args], cwd=cwd, check=True, capture_output=True, text=True)


@pytest.fixture
def history_repo(tmp_path: Path) -> Path:
    """A repo where ``gone.py`` was committed, then deleted, two commits later."""
    repo = tmp_path / "origin"
    repo.mkdir()
    _git(repo, "init", "-q")
    (repo / "gone.py").write_text("x = 1\n", encoding="utf-8")
    _git(repo, "add", "gone.py")
    _git(repo, "commit", "-q", "-m", "add gone.py")
    (repo / "kept.py").write_text("y = 2\n", encoding="utf-8")
    _git(repo, "add", "kept.py")
    _git(repo, "commit", "-q", "-m", "add kept.py")
    _git(repo, "rm", "-q", "gone.py")
    _git(repo, "commit", "-q", "-m", "delete gone.py")
    return repo


def test_full_history_still_classifies_a_deleted_file_historical(history_repo: Path) -> None:
    assert classify_citation("gone.py", repo_root=history_repo) == "historical"


def test_shallow_clone_raises_instead_of_calling_history_unresolved(
    history_repo: Path, tmp_path: Path
) -> None:
    shallow = tmp_path / "shallow"
    subprocess.run(
        ["git", "clone", "-q", "--depth", "1", history_repo.as_uri(), str(shallow)],
        check=True, capture_output=True, text=True,
    )
    with pytest.raises(CitationHistoryUnavailableError, match="git fetch --unshallow"):
        classify_citation("gone.py", repo_root=shallow)


def test_shallow_clone_still_answers_questions_that_need_no_history(
    history_repo: Path, tmp_path: Path
) -> None:
    """Only the history question needs full history: a present file is current."""
    shallow = tmp_path / "shallow"
    subprocess.run(
        ["git", "clone", "-q", "--depth", "1", history_repo.as_uri(), str(shallow)],
        check=True, capture_output=True, text=True,
    )
    assert classify_citation("kept.py", repo_root=shallow) == "current"


def test_a_failing_git_command_raises_instead_of_answering_no(tmp_path: Path) -> None:
    """Not a repository: git exits fatally. The old helpers read that as
    "not tracked / not ignored / never existed" and classified ``unresolved``."""
    not_a_repo = tmp_path / "plain"
    not_a_repo.mkdir()
    with pytest.raises(CitationHistoryUnavailableError):
        classify_citation("missing.py", repo_root=not_a_repo)


def test_a_relative_citation_that_leaves_the_repo_stays_unresolved(history_repo: Path) -> None:
    """``../x`` is outside the tree; git answers it with a fatal "outside
    repository", which is not a history failure — the classifier says
    ``unresolved`` (the pre-change verdict), not a mislabelled git error."""
    assert classify_citation("../outside_zz.py", repo_root=history_repo) == "unresolved"


@pytest.mark.parametrize("helper", [_is_ignored, _existed_ever], ids=["is_ignored", "existed_ever"])
def test_each_history_helper_raises_on_a_fatal_git_exit(tmp_path: Path, helper) -> None:
    not_a_repo = tmp_path / "plain"
    not_a_repo.mkdir()
    with pytest.raises(CitationHistoryUnavailableError):
        helper("missing.py", not_a_repo)
