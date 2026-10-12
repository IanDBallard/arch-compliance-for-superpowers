"""Append-only efficacy ledger (spec: Efficacy ledger)."""
import json
import re
from pathlib import Path

import pytest
from pydantic import ValidationError

from acf.adr.ledger import (
    LEDGER_PATH,
    LEDGER_PREAMBLE,
    LedgerAmendment,
    LedgerRow,
    append_amendment,
    append_row,
)
from acf.exceptions import LedgerWriteError

#: The eleven "recorded BEFORE dispatch" predictor fields. Hoisted to a module
#: constant and reused both as the parametrize source AND inside the test body
#: (see test_every_pre_dispatch_predictor_is_required) so a name added here is
#: mechanically checked against the model's own required/default state rather
#: than trusted by inspection.
_PRE_DISPATCH = (
    "spec_path", "commit_sha", "date", "spec_kinds", "new_design_elements",
    "phases", "cited_files", "touched_surfaces", "surface_call_sites",
    "filter_would_skip", "holdout",
)


def _row(**overrides) -> LedgerRow:
    fields = {
        "spec_path": "docs/design/TOPIC.md",
        "commit_sha": "03fdaa83",
        "date": "2026-08-10",
        "spec_kinds": ["defect"],
        "new_design_elements": 7,
        "phases": 3,
        "cited_files": 12,
        "touched_surfaces": ["persistence_format"],
        "surface_call_sites": 20,
        "filter_would_skip": False,
        "holdout": False,
        "outcome": "BLOCKED",
        "findings_by_lens_severity": {"refuter": {"blocking": 3, "important": 1}},
        "converged_count": 1,
        "absorbed": 0,
        "rejected": 0,
        "blocks_overturned": 0,
        "tokens": 526000,
        "wall_clock_s": 960,
    }
    fields.update(overrides)
    return LedgerRow(**fields)


def _amendment(**overrides) -> LedgerAmendment:
    fields = {
        "spec_path": "docs/design/TOPIC.md",
        "commit_sha": "03fdaa83",
        "date": "2026-08-10",
    }
    fields.update(overrides)
    return LedgerAmendment(**fields)


def test_ledger_path_is_the_spec_location():
    assert LEDGER_PATH == "docs/reviews/adversarial_design_ledger.jsonl"


def test_escapes_defaults_to_zero():
    assert _row().escapes == 0


def test_spec_path_must_be_posix():
    with pytest.raises(ValidationError, match="POSIX"):
        _row(spec_path=r"docs\design\TOPIC.md")


@pytest.mark.parametrize("missing", _PRE_DISPATCH)
def test_every_pre_dispatch_predictor_is_required(missing: str):
    # Model-derived tripwire, not a copy of the parametrize list: if a
    # defaulted field (e.g. "escapes") were ever added to _PRE_DISPATCH, this
    # assertion — which asks the MODEL whether the field is required, rather
    # than comparing two independently hand-typed literal lists — would catch
    # it. A defaulted field's parametrize case would otherwise pass the
    # decorator silently and only fail (correctly, but without explanation)
    # deep inside pytest.raises("DID NOT RAISE").
    assert not {n for n in _PRE_DISPATCH if not LedgerRow.model_fields[n].is_required()}
    fields = _row().model_dump()
    del fields[missing]
    with pytest.raises(ValidationError):
        LedgerRow(**fields)


def test_tokens_and_wall_clock_reject_zero():
    # The v6 run (2026-08-11) wrote tokens=0 into the row — a placeholder in
    # the one field the "is this gate worth its cost?" question depends on,
    # against a SKILL.md instruction that already said "round, do not fabricate
    # a number you did not measure". The instruction did not hold, so the
    # contract enforces it: a four-reviewer run cannot cost zero tokens or take
    # zero seconds, and an unmeasured value must fail loudly at construction
    # rather than silently corrupt the cost series (528k, 691k, 0).
    for field in ("tokens", "wall_clock_s"):
        with pytest.raises(ValidationError):
            _row(**{field: 0})


def test_date_is_a_passed_in_iso_string_not_computed():
    row = _row(date="2026-08-10")
    assert row.date == "2026-08-10"
    with pytest.raises(ValidationError, match="ISO"):
        _row(date="10/08/2026")


def test_date_rejects_a_calendar_invalid_date():
    # Shaped like an ISO date (matches the regex) but not a real calendar
    # date. The regex alone would accept this; datetime.date.fromisoformat
    # does not. Reads no clock, so this does not violate "date is passed in,
    # never computed" — it validates the passed-in value, it does not supply one.
    with pytest.raises(ValidationError, match="ISO"):
        _row(date="2026-13-45")


def test_spec_kinds_rejects_empty_list():
    # An empty list is a "required predictor" recorded empty — exactly what a
    # caller that failed to classify the spec would emit by omission.
    with pytest.raises(ValidationError):
        _row(spec_kinds=[])


def test_touched_surfaces_rejects_empty_list():
    # touched_surfaces=[] would be a second encoding of the "none" literal
    # TouchedSurface already declares; forcing at least one entry means "none"
    # is the one and only way to record "touched nothing".
    with pytest.raises(ValidationError):
        _row(touched_surfaces=[])


def test_public_interface_is_a_recordable_surface():
    # GEMINI.md item 8 names "a public interface" in the gate's trigger list, and
    # filter_would_skip is derived from touched_surfaces against exactly that list
    # (SKILL.md). Without a member for it, a public-interface-only spec has no
    # truthful value to record and lands as filter_would_skip=true — asserting the
    # narrowed filter would SKIP a spec it would in fact KEEP, biasing the one
    # number the narrowing decision rests on.
    row = _row(touched_surfaces=["public_interface"])
    assert row.touched_surfaces == ["public_interface"]


def test_an_unlisted_touched_surface_is_rejected():
    # Pairs with the test above: acceptance of "public_interface" only means
    # something because the set is closed. If TouchedSurface were widened to a
    # bare str, the test above would pass for the wrong reason.
    with pytest.raises(ValidationError):
        _row(touched_surfaces=["public_api"])


def test_findings_by_lens_severity_key_must_be_a_known_reviewer():
    # The lens key is tallied by eye; a typo'd reviewer name would silently
    # open a second bucket for the same lens instead of failing loudly.
    with pytest.raises(ValidationError):
        _row(findings_by_lens_severity={"reftuer": {"blocking": 1}})


@pytest.mark.parametrize("field", ["spec_path", "commit_sha"])
def test_free_text_fields_reject_backslash_or_stay_out_of_the_file(field, tmp_path: Path):
    # Attempts a backslash in each free-text field and requires ONE of two
    # outcomes: construction refuses it outright, or (if some future change
    # ever loosened the field's type) the value still never reaches the file.
    # A fixture with no backslash anywhere (the original version of this
    # test) stays green even if the POSIX guard on the field were deleted —
    # this version cannot: it manufactures the exact input the guard exists
    # to catch.
    path = tmp_path / "ledger.jsonl"
    try:
        row = _row(**{field: "has\\backslash"})
    except ValidationError:
        return  # construction refused the backslash — the property holds
    append_row(row, path)
    assert "\\" not in path.read_text(encoding="utf-8")


def test_creating_the_file_writes_the_preamble_first(tmp_path: Path):
    path = tmp_path / "ledger.jsonl"
    append_row(_row(), path)
    lines = path.read_text(encoding="utf-8").splitlines()
    assert json.loads(lines[0]) == LEDGER_PREAMBLE
    assert "proxy" in LEDGER_PREAMBLE["_comment"]
    assert json.loads(lines[1])["spec_path"] == "docs/design/TOPIC.md"


def test_preamble_documents_the_amendment_rule():
    # The plan's ruling on the post-hoc-counter contradiction (append-only
    # module, but the brief said counters get "amended"): amendments are a
    # superseding row, never a rewrite. The file documents its own reading
    # rule so a future reader of raw JSONL knows to take the LAST row for a
    # given spec, not the first.
    assert "superseding" in LEDGER_PREAMBLE["_comment"]
    assert "LAST" in LEDGER_PREAMBLE["_comment"]


def test_preamble_uses_compact_separators_matching_row_lines(tmp_path: Path):
    path = tmp_path / "ledger.jsonl"
    append_row(_row(), path)
    preamble_line = path.read_text(encoding="utf-8").splitlines()[0]
    spaced = json.dumps(LEDGER_PREAMBLE, ensure_ascii=False)          # default separators
    compact = json.dumps(LEDGER_PREAMBLE, ensure_ascii=False, separators=(",", ":"))
    assert preamble_line == compact
    assert preamble_line != spaced


def test_preexisting_zero_byte_file_still_gets_the_preamble(tmp_path: Path):
    # A file that exists but is empty (touch'd, a crashed first run, a
    # checked-in empty placeholder) must still receive the preamble.
    # `not target.exists()` alone is False for a 0-byte file and would
    # permanently skip the warning for that file's entire lifetime.
    path = tmp_path / "ledger.jsonl"
    path.touch()
    append_row(_row(), path)
    lines = path.read_text(encoding="utf-8").splitlines()
    assert json.loads(lines[0]) == LEDGER_PREAMBLE
    assert json.loads(lines[1])["spec_path"] == "docs/design/TOPIC.md"


def test_appending_does_not_rewrite_the_preamble(tmp_path: Path):
    path = tmp_path / "ledger.jsonl"
    append_row(_row(), path)

    # Tamper with the on-disk preamble line so its bytes no longer match a
    # fresh serialization of LEDGER_PREAMBLE. If append_row ever regenerated
    # line 0 from the constant (e.g. a "rewrite the whole file" implementation
    # that reproduces line 0 from the in-memory constant every call), this
    # tamper marker would be silently overwritten and the assertion below
    # would catch it. Asserting len(lines) == 3 alone would NOT catch that
    # failure mode, because a rewrite that happens to reproduce identical
    # preamble bytes also yields three lines.
    lines_on_disk = path.read_text(encoding="utf-8").splitlines()
    tampered_preamble = json.dumps({**LEDGER_PREAMBLE, "_tamper_marker": "should-survive"})
    lines_on_disk[0] = tampered_preamble
    path.write_text("\n".join(lines_on_disk) + "\n", encoding="utf-8")

    append_row(_row(spec_path="docs/design/OTHER.md"), path)

    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 3
    assert json.loads(lines[0])["_tamper_marker"] == "should-survive"
    assert json.loads(lines[2])["spec_path"] == "docs/design/OTHER.md"


def test_existing_content_is_never_truncated(tmp_path: Path):
    path = tmp_path / "ledger.jsonl"
    append_row(_row(), path)
    append_row(_row(spec_path="docs/design/OTHER.md"), path)

    # Write a line append_row itself never wrote, directly to the file. A
    # broken implementation that keeps its own in-memory list of rows and
    # rewrites the file from that list on every call (rather than truly
    # opening in append mode) has no way to know this line exists, so it
    # would be dropped on the next append_row call. A plain `startswith`
    # against a `before` snapshot taken without this external write would
    # pass vacuously under such an implementation, as long as its
    # regenerated bytes happened to match; injecting content append_row
    # cannot have produced closes that gap.
    with path.open("a", encoding="utf-8") as fh:
        fh.write('{"external": "written-outside-append_row"}\n')
    tampered = path.read_text(encoding="utf-8")

    append_row(_row(spec_path="docs/design/THIRD.md"), path)

    after = path.read_text(encoding="utf-8")
    assert after.startswith(tampered)
    assert json.loads(after.splitlines()[-1])["spec_path"] == "docs/design/THIRD.md"


def test_append_grows_file_by_exactly_the_new_row_bytes(tmp_path: Path):
    # A general content invariant: a successful append changes the file's
    # size by exactly the new row's bytes plus one newline — no double
    # writes, no dropped bytes, no extra blank lines. NOTE: this assertion
    # alone does NOT distinguish true append from a content-preserving
    # slurp-and-reopen-in-"w" writer (verified empirically — see
    # test_append_never_truncates_the_underlying_file below, and the fix
    # report's correction of this point). A slurp-then-rewrite that
    # reproduces existing bytes exactly and then adds the same new bytes
    # ends at the same final size as a true append; the size delta cannot
    # tell them apart. Kept as a real, independently useful invariant, not
    # as the mechanism that closes the read-modify-write finding.
    path = tmp_path / "ledger.jsonl"
    append_row(_row(), path)
    size_before = path.stat().st_size
    new_row = _row(spec_path="docs/design/OTHER.md")
    append_row(new_row, path)
    size_after = path.stat().st_size
    expected_growth = len(new_row.model_dump_json().encode("utf-8")) + 1  # + trailing "\n"
    assert size_after - size_before == expected_growth


def test_append_never_truncates_the_underlying_file(tmp_path: Path, monkeypatch):
    # The mechanism-level test for the read-modify-write finding: a
    # slurp-and-reopen-in-"w" writer is content-preserving on success (so
    # byte-growth and tamper-survival assertions can't distinguish it from a
    # true append — confirmed by replaying both against such a stub) but it
    # is only safe because it happens not to crash between truncate and
    # write. The actual defect is the truncating open() call itself: this
    # test spies on every Path.open() call append_row makes and asserts none
    # of them request a truncating/write mode ("w", "wb", "w+", etc).
    path = tmp_path / "ledger.jsonl"
    append_row(_row(), path)  # create the file uncontested, before the spy attaches

    modes_used: list[str] = []
    real_open = Path.open

    def _spy_open(self, *args, **kwargs):
        mode = args[0] if args else kwargs.get("mode", "r")
        modes_used.append(mode)
        return real_open(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", _spy_open)
    append_row(_row(spec_path="docs/design/OTHER.md"), path)

    # The spy MUST have fired. Without this line the test is vacuous: a writer
    # that used builtin open(target, "w") instead of Path.open never trips the
    # spy, leaving modes_used empty, so `not truncating` is trivially True and
    # the read-modify-write this test exists to forbid passes it. Verified by
    # substituting exactly that writer — with this assertion the test goes RED,
    # without it, green.
    assert modes_used, "spy never fired: append_row no longer routes through Path.open"
    truncating = [m for m in modes_used if "w" in m and "a" not in m]
    assert not truncating, f"append_row opened the file in a truncating mode: {modes_used!r}"


def test_each_row_is_one_line_of_valid_json(tmp_path: Path):
    path = tmp_path / "ledger.jsonl"
    append_row(_row(), path)
    append_row(_row(outcome="CLEARED"), path)
    for line in path.read_text(encoding="utf-8").splitlines():
        assert json.loads(line)


def test_holdout_rows_are_distinguishable(tmp_path: Path):
    path = tmp_path / "ledger.jsonl"
    append_row(_row(filter_would_skip=True, holdout=True), path)
    row = json.loads(path.read_text(encoding="utf-8").splitlines()[1])
    assert row["filter_would_skip"] is True
    assert row["holdout"] is True


def test_unwritable_path_raises_ledger_write_error(tmp_path: Path):
    # A directory where the file should be: the open() fails, and we must not
    # skip. Verified on this platform (Windows): opening a directory path in
    # "a" mode raises PermissionError, a subclass of OSError, NOT silently
    # succeeding — so append_row's `except OSError` clause is genuinely
    # exercised here, and this test would fail (no LedgerWriteError raised)
    # if append_row ever swallowed the OSError instead of re-raising it.
    path = tmp_path / "ledger.jsonl"
    path.mkdir()
    with pytest.raises(LedgerWriteError, match="ledger.jsonl"):
        append_row(_row(), path)


def test_unwritable_path_error_message_is_absolute(tmp_path: Path, monkeypatch):
    # A relative path in the error message gives no indication of the cwd it
    # was resolved against. Passing a RELATIVE Path into append_row must still
    # produce an absolute path in the raised message.
    monkeypatch.chdir(tmp_path)
    rel_path = Path("ledger.jsonl")
    rel_path.mkdir()
    expected_absolute = (tmp_path / "ledger.jsonl").absolute().as_posix()
    with pytest.raises(LedgerWriteError, match=re.escape(expected_absolute)):
        append_row(_row(), rel_path)


def test_missing_parent_directory_is_created(tmp_path: Path):
    path = tmp_path / "docs" / "reviews" / "ledger.jsonl"
    append_row(_row(), path)
    assert path.is_file()


def test_ledger_bytes_use_unix_newlines_not_crlf(tmp_path: Path):
    # Every other assertion in this file reads through Path.read_text(), which
    # applies universal-newline translation and would hide a CRLF-writing
    # regression. Read raw bytes instead.
    path = tmp_path / "ledger.jsonl"
    append_row(_row(), path)
    append_row(_row(spec_path="docs/design/OTHER.md"), path)
    assert b"\r" not in path.read_bytes()


def test_non_ascii_values_are_written_as_utf8_bytes(tmp_path: Path):
    # If encoding="utf-8" were dropped, `open()` would fall back to the
    # platform's preferred encoding (commonly cp1252 on Windows), which
    # encodes "É" as a single byte (0xC9) rather than UTF-8's two bytes
    # (0xC3 0x89) — a silent corruption no ASCII-only fixture would surface.
    path = tmp_path / "ledger.jsonl"
    append_row(_row(spec_path="docs/design/CAFÉ.md"), path)
    raw = path.read_bytes()
    assert "CAFÉ".encode("utf-8") in raw


# --- LedgerAmendment / append_amendment (superseding record, never a rewrite) ---


def test_amendment_appends_without_touching_preamble_or_prior_rows(tmp_path: Path):
    # Content-based check only: the bytes already on disk (preamble + the
    # original row) must survive byte-for-byte, with the amendment landing as
    # a NEW third line. NOTE: this is NOT the mechanism-level guarantee — a
    # slurp-and-reopen-in-"w" writer is content-preserving on success and
    # would pass every assertion here too (the same caveat
    # test_append_grows_file_by_exactly_the_new_row_bytes documents for
    # append_row). See
    # test_amendment_append_never_truncates_the_underlying_file below for the
    # mode-spy test that actually distinguishes true append from that failure
    # mode on this entry point.
    path = tmp_path / "ledger.jsonl"
    append_row(_row(), path)
    before = path.read_text(encoding="utf-8")
    append_amendment(_amendment(escapes=1), path)
    after = path.read_text(encoding="utf-8")
    assert after.startswith(before)
    lines = after.splitlines()
    assert len(lines) == 3
    assert json.loads(lines[2])["escapes"] == 1


def test_amendment_append_never_truncates_the_underlying_file(tmp_path: Path, monkeypatch):
    # Twin of test_append_never_truncates_the_underlying_file for the
    # append_amendment entry point (2026-08-10 review finding: the
    # content-based test above cannot catch a truncating write — a
    # slurp-and-reopen-in-"w" writer is content-preserving on success — and
    # append_amendment had no mode-spy of its own, so nothing but a human
    # noticing the shared _append_json_line helper protected this path).
    # Spies on every Path.open() call append_amendment makes and asserts none
    # of them request a truncating/write mode ("w", "wb", "w+", etc).
    path = tmp_path / "ledger.jsonl"
    append_row(_row(), path)  # create the file uncontested, before the spy attaches

    modes_used: list[str] = []
    real_open = Path.open

    def _spy_open(self, *args, **kwargs):
        mode = args[0] if args else kwargs.get("mode", "r")
        modes_used.append(mode)
        return real_open(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", _spy_open)
    append_amendment(_amendment(escapes=1), path)

    # See the twin assertion in test_append_never_truncates_the_underlying_file:
    # an empty modes_used makes every downstream assertion vacuous, which is how
    # a builtin-open() read-modify-write left 10/10 append-only tests green.
    assert modes_used, (
        "spy never fired: append_amendment no longer routes through Path.open"
    )
    truncating = [m for m in modes_used if "w" in m and "a" not in m]
    assert not truncating, (
        f"append_amendment opened the file in a truncating mode: {modes_used!r}"
    )


def test_amendment_counters_are_all_optional(tmp_path: Path):
    # An amender "sets only what it knows" — constructing with NO counters at
    # all must succeed (all four default to None), and setting only one must
    # leave the other three None rather than forcing a caller to know or
    # re-derive them. If any counter were made required, both constructions
    # below would raise ValidationError instead of returning.
    bare = _amendment()
    assert bare.absorbed is None
    assert bare.rejected is None
    assert bare.blocks_overturned is None
    assert bare.escapes is None

    partial = _amendment(escapes=2)
    assert partial.escapes == 2
    assert partial.absorbed is None
    assert partial.rejected is None
    assert partial.blocks_overturned is None


@pytest.mark.parametrize("field", ["spec_path", "commit_sha"])
def test_amendment_free_text_fields_reject_backslash_or_stay_out_of_the_file(
    field, tmp_path: Path
):
    # Twin of test_free_text_fields_reject_backslash_or_stay_out_of_the_file
    # for LedgerAmendment (2026-08-10 review finding: LedgerRow's equivalent
    # test is parametrized over both fields; the amendment test previously
    # covered only spec_path, leaving commit_sha's identical PosixStr
    # annotation asserted by inspection rather than by a test). Same two-outcome
    # contract: construction refuses the backslash outright, or — if some
    # future change ever loosened the field's type — the value still never
    # reaches the file.
    path = tmp_path / "ledger.jsonl"
    try:
        amendment = _amendment(**{field: "has\\backslash"})
    except ValidationError:
        return  # construction refused the backslash — the property holds
    append_amendment(amendment, path)
    assert "\\" not in path.read_text(encoding="utf-8")


def test_amendment_date_rejects_a_calendar_invalid_date():
    # Same regex-shaped-but-not-a-real-date trap as LedgerRow's date field:
    # "2026-13-45" matches \d{4}-\d{2}-\d{2} but month 13 / day 45 do not
    # exist. Only the shared datetime.date.fromisoformat check catches this.
    with pytest.raises(ValidationError, match="ISO"):
        _amendment(date="2026-13-45")


def test_amendment_rejects_an_unknown_field():
    # extra="forbid" (Architectural Contract 5's convention throughout this
    # module): a fabricated or typo'd key must fail loudly at construction,
    # not be silently dropped.
    with pytest.raises(ValidationError):
        _amendment(fabricated_field="x")


def test_amendment_unwritable_path_raises_ledger_write_error(tmp_path: Path):
    path = tmp_path / "ledger.jsonl"
    path.mkdir()
    with pytest.raises(LedgerWriteError, match="ledger.jsonl"):
        append_amendment(_amendment(escapes=1), path)


def test_file_with_amendment_remains_valid_jsonl_and_is_distinguishable_from_a_row(
    tmp_path: Path,
):
    path = tmp_path / "ledger.jsonl"
    append_row(_row(), path)
    append_amendment(_amendment(rejected=2), path)
    append_row(_row(spec_path="docs/design/OTHER.md"), path)

    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 4  # preamble + row + amendment + row
    parsed = [json.loads(line) for line in lines]

    amendment_record = parsed[2]
    assert amendment_record["rejected"] == 2
    # A LedgerRow always carries its pre-dispatch predictors; an amendment
    # never does — it shares only the run-identity fields (spec_path,
    # commit_sha, date) used to match it to the original row. If
    # append_amendment ever serialized a LedgerAmendment padded out with the
    # row's OTHER fields (making it "look like a truncated row" rather than
    # its own record type), this would catch it.
    identity_fields = {"spec_path", "commit_sha", "date"}
    for predictor in _PRE_DISPATCH:
        if predictor in identity_fields:
            continue
        assert predictor not in amendment_record


# --- LedgerRow.refuted_carryover / refuted_delta (M5 schema) ---


def test_carryover_counters_default_to_none():
    # None = unknown (a first run); never write 0 as a stand-in for unknown.
    row = _row()
    assert row.refuted_carryover is None
    assert row.refuted_delta is None


def test_carryover_counters_accept_paired_values():
    row = _row(refuted_carryover=1, refuted_delta=2)
    assert (row.refuted_carryover, row.refuted_delta) == (1, 2)
    # A CLEARED re-run writes measured zeros — 0/0 is a legal pair.
    zeros = _row(refuted_carryover=0, refuted_delta=0)
    assert (zeros.refuted_carryover, zeros.refuted_delta) == (0, 0)


def test_carryover_counters_reject_one_counter_set():
    for overrides in ({"refuted_carryover": 1}, {"refuted_delta": 0}):
        with pytest.raises(ValidationError, match="set together"):
            _row(**overrides)


def test_carryover_counters_reject_negative():
    with pytest.raises(ValidationError):
        _row(refuted_carryover=-1, refuted_delta=0)


def test_full_dump_round_trips():
    # No prior test round-trips a complete dump (the :90-93 test deletes a
    # field to assert failure); this pins that optional additions round-trip.
    for row in (_row(), _row(refuted_carryover=1, refuted_delta=2)):
        assert LedgerRow(**row.model_dump()) == row

def test_a_real_host_ledger_record_still_validates():
    """A record written by the origin, before the port, must still load.

    Copied verbatim from a host ledger (HistoricMansions
    ``docs/reviews/adversarial_design_ledger.jsonl`` line 329 at ``d2ce43a9``).
    If this fails, the port changed the persisted format, which is forbidden.
    The round-trip asserts no field was renamed, dropped or re-defaulted.
    """
    from acf.adr.ledger import LedgerRow

    line = '{"spec_path":"docs/design/SEQ_CAPTION_READER.md","commit_sha":"b9216196c5782a869526f1ea1486f9d892fd9c02","date":"2026-10-10","spec_kinds":["defect"],"new_design_elements":17,"phases":2,"cited_files":86,"touched_surfaces":["public_interface"],"surface_call_sites":19,"filter_would_skip":false,"holdout":false,"outcome":"BLOCKED","findings_by_lens_severity":{"refuter":{"blocking":0,"important":1,"advisory":4},"compliance":{"blocking":0,"important":0,"advisory":4},"sweeper":{"blocking":3,"important":1,"advisory":5},"hardening":{"blocking":0,"important":2,"advisory":3}},"converged_count":2,"absorbed":0,"rejected":0,"blocks_overturned":0,"tokens":727773,"wall_clock_s":798,"escapes":0,"refuted_carryover":0,"refuted_delta":3}'
    row = json.loads(line)
    assert row, "paste a real record before running this"
    parsed = LedgerRow.model_validate(row)
    assert parsed.spec_path
    assert parsed.outcome
    assert parsed.model_dump(mode="json") == row
