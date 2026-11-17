import pytest
from acf.exceptions import AcfInputError
from acf.review import doctrine_section

DOC = "# T\n## A\na1\n### A.1\na2\n## B\nb\n"


def test_section_stops_at_same_or_higher_heading():
    assert doctrine_section(DOC, "## A", mandate_id="m") == "## A\na1\n### A.1\na2"


def test_non_heading_anchor_stops_at_any_heading():
    assert doctrine_section(DOC, "a1", mandate_id="m") == "a1"


def test_unresolved_anchor_names_mandate():
    with pytest.raises(AcfInputError, match="'m'.*## Z"):
        doctrine_section(DOC, "## Z", mandate_id="m")
