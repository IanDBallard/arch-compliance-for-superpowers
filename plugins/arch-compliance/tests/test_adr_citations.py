"""Citation classification, against a git history this test builds.

The origin's version of these tests asserted verdicts about its own tracked
files, deleted files and ignored paths - facts about one repository, which
cannot travel. Here the history is constructed instead. The fixture reproduces
each condition the origin's assertions depended on, under the SAME path
strings, so every assertion below is the origin's, unchanged; only the
repository it runs against differs.

Provenance of the kinds (from the origin):

- **historical** - "commit 4594501a touches only ``scripts/ai/file_tracker.py``"
  is a true statement about the past; that file was deleted later. This is the
  case that hard-failed the gate on 2026-08-11.
- **proposed** - ``normalize_collection_order.py`` is the command the spec
  exists to introduce.
- **external** - live book roots and gitignored build artifacts.

The requirement was never "the path exists". It is "the reviewer knows what
kind of path it is being handed".
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from acf.adr.citations import (
    classify_citation,
    classify_citations,
    count_cited_files,
    resolve_citation,
    unresolved_citations,
)


def _git(repo: Path, *args: str, empty_config: Path) -> None:
    subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        env={
            **os.environ,
            # Hermetic: no user/system config, so no global hooks, signing or
            # autocrlf settings can change what the fixture records.
            "GIT_CONFIG_GLOBAL": str(empty_config),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_AUTHOR_NAME": "t",
            "GIT_AUTHOR_EMAIL": "t@t",
            "GIT_COMMITTER_NAME": "t",
            "GIT_COMMITTER_EMAIL": "t@t",
        },
    )


def _write(repo: Path, rel: str, text: str = "x = 1\n") -> None:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture(scope="module")
def REPO(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """A repository holding every condition the origin's assertions relied on.

    - ``scripts/core/exceptions.py`` is tracked: the current / suffix / basename cases.
    - ``scripts/cms_server/routes/content.py`` is tracked, so the wrong path
      ``scripts/api/routes/content.py`` is a near miss, not a trivial absence.
    - ``scripts/ai/file_tracker.py`` was committed, then deleted: historical.
    - ``.gitignore`` carries ``build/`` and ``check_*.py``. ``build/md/book.md``
      matches the ignore pattern and is NOT on disk - as in the origin, where
      build output lives elsewhere. (An ignored file that exists classifies
      ``current``: existence is tested before the ignore check.) And
      ``scripts/maintenance/check_book_tier_drift.py`` is force-tracked, so its
      bare name matches an ignore pattern while the file itself is tracked.
    """
    root = tmp_path_factory.mktemp("citations")
    empty_config = root / "empty.gitconfig"
    empty_config.write_text("", encoding="utf-8")
    repo = root / "host"
    repo.mkdir()
    g = lambda *a: _git(repo, *a, empty_config=empty_config)  # noqa: E731

    g("init", "-q")
    _write(repo, ".gitignore", "build/\ncheck_*.py\n")
    _write(repo, "scripts/core/exceptions.py")
    _write(repo, "scripts/cms_server/routes/content.py")
    _write(repo, "scripts/ai/file_tracker.py")
    _write(repo, "scripts/maintenance/check_book_tier_drift.py")
    g("add", "-A")
    g("add", "-f", "scripts/maintenance/check_book_tier_drift.py")
    g("commit", "-qm", "initial tree")
    (repo / "scripts/ai/file_tracker.py").unlink()
    g("add", "-A")
    g("commit", "-qm", "delete file_tracker")
    return repo


def test_a_file_in_the_tree_is_current(REPO):
    assert classify_citation("scripts/core/exceptions.py", repo_root=REPO) == "current"


def test_a_line_suffix_is_stripped_before_resolution(REPO):
    # Citations arrive as file:line and file:line-range.
    assert classify_citation("scripts/core/exceptions.py:10", repo_root=REPO) == "current"
    assert classify_citation("scripts/core/exceptions.py:10-20", repo_root=REPO) == "current"


def test_a_deleted_file_is_historical_not_unresolved(REPO):
    # THE v7 CASE: the spec cites a since-deleted file in a true statement
    # about what an earlier commit touched.
    assert classify_citation("scripts/ai/file_tracker.py", repo_root=REPO) == "historical"


def test_a_declared_proposed_path_is_proposed_even_though_absent(REPO):
    proposed = frozenset({"scripts/maintenance/normalize_collection_order.py"})
    assert classify_citation(
        "scripts/maintenance/normalize_collection_order.py",
        repo_root=REPO, proposed=proposed,
    ) == "proposed"


def test_proposed_wins_over_history_so_a_revived_name_is_not_mistaken(REPO):
    # A spec proposing a path that once existed means the NEW file, not the old
    # one - the spec's own declaration outranks the archaeology.
    proposed = frozenset({"scripts/ai/file_tracker.py"})
    assert classify_citation(
        "scripts/ai/file_tracker.py", repo_root=REPO, proposed=proposed,
    ) == "proposed"


def test_gitignored_build_artifacts_are_external(REPO):
    assert classify_citation("build/md/book.md", repo_root=REPO) == "external"


def test_an_absolute_path_outside_the_repo_is_external(REPO):
    assert classify_citation("G:/My Drive/Arduino/Projects", repo_root=REPO) == "external"


def test_a_path_that_never_existed_is_unresolved(REPO):
    assert classify_citation(
        "scripts/core/no_such_module_ever.py", repo_root=REPO,
    ) == "unresolved"


def test_classify_citations_maps_every_input(REPO):
    result = classify_citations(
        ["scripts/core/exceptions.py:1", "scripts/ai/file_tracker.py",
         "scripts/core/no_such_module_ever.py"],
        repo_root=REPO,
    )
    assert result["scripts/core/exceptions.py:1"] == "current"
    assert result["scripts/ai/file_tracker.py"] == "historical"
    assert result["scripts/core/no_such_module_ever.py"] == "unresolved"


def test_a_tracked_file_beats_a_gitignore_pattern_match_on_its_bare_name(REPO):
    # `.gitignore` carries `check_*.py`, so `git check-ignore` matches the BARE
    # NAME `check_book_tier_drift.py` - and when the ignore test ran before
    # suffix resolution, a file tracked at
    # scripts/maintenance/check_book_tier_drift.py was handed to reviewers as
    # "external". A tracked file is by definition not ignored. Resolution wins.
    assert classify_citation(
        "check_book_tier_drift.py", repo_root=REPO,
    ) == "current"


def test_a_path_the_spec_cites_as_nonexistent_is_asserted_absent(REPO):
    # Some citations exist BECAUSE the path does not. The absence is the
    # finding, declared off the spec like `proposed` rather than guessed.
    absent = frozenset({"collection.20260806-221109-183161.yml"})
    assert classify_citation(
        "collection.20260806-221109-183161.yml", repo_root=REPO, asserted_absent=absent,
    ) == "asserted_absent"


def test_asserted_absent_does_not_suppress_a_genuine_unresolved_path(REPO):
    # Declaring one path absent must not blanket-excuse the rest.
    absent = frozenset({"collection.20260806-221109-183161.yml"})
    assert classify_citation(
        "scripts/api/routes/content.py", repo_root=REPO, asserted_absent=absent,
    ) == "unresolved"


def test_a_bare_basename_used_as_prose_shorthand_resolves(REPO):
    # Specs name a file in full once and then refer to it by basename.
    assert classify_citation("exceptions.py", repo_root=REPO) == "current"


def test_a_partial_path_suffix_matches_the_tracked_file(REPO):
    assert classify_citation("core/exceptions.py", repo_root=REPO) == "current"


def test_suffix_resolution_does_not_rescue_a_genuinely_wrong_path(REPO):
    # The discriminating case, and the reason this must be a SUFFIX match and
    # not a fuzzy one: the tree has scripts/cms_server/routes/content.py, and
    # "api/routes/content.py" is not a suffix of it, so it stays unresolved.
    assert classify_citation(
        "scripts/api/routes/content.py", repo_root=REPO,
    ) == "unresolved"


def test_resolve_citation_returns_the_full_path_for_the_reviewer(REPO):
    # The controller hands reviewers the resolved path, not the lookup.
    kind, resolved = resolve_citation("exceptions.py", repo_root=REPO)
    assert kind == "current"
    assert resolved == "scripts/core/exceptions.py"


def test_resolve_citation_leaves_an_exact_path_untouched(REPO):
    kind, resolved = resolve_citation("scripts/core/exceptions.py:12", repo_root=REPO)
    assert kind == "current"
    assert resolved == "scripts/core/exceptions.py"


def test_cited_files_counts_unique_paths_not_citation_occurrences():
    # Counting is the function's job, not the controller's judgement: the
    # ledger predictor drifted between runs when it was left to judgement.
    assert count_cited_files([
        "scripts/core/exceptions.py:10",     # same file, three citations
        "scripts/core/exceptions.py:20",
        "scripts/core/exceptions.py",
        "scripts/core/collection_service.py:1",
    ]) == 2


def test_cited_files_counts_every_kind_not_only_current():
    # historical / proposed / external paths are real citations the reviewers
    # were handed; excluding them would undercount the spec's evidential reach.
    assert count_cited_files([
        "scripts/core/exceptions.py",
        "scripts/ai/file_tracker.py",
        "build/md/book.md",
    ]) == 3


def test_only_unresolved_citations_are_returned_for_the_hard_fail(REPO):
    # The gate aborts on these and ONLY these.
    unresolved = unresolved_citations(
        ["scripts/core/exceptions.py", "scripts/ai/file_tracker.py",
         "build/md/book.md", "scripts/core/no_such_module_ever.py"],
        repo_root=REPO,
    )
    assert unresolved == ["scripts/core/no_such_module_ever.py"]
