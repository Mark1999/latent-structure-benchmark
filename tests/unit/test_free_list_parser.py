"""Tests for the free-list parser in isolation."""

from pathlib import Path

from cdb_collect.protocol.free_list import parse_free_list

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def test_parse_numbered_list():
    text = "1. Mother\n2. Father\n3. Sister\n4. Brother\n5. Aunt"
    items, raw = parse_free_list(text, truncation_k=25)
    assert items == ["mother", "father", "sister", "brother", "aunt"]
    assert len(raw) == 5


def test_parse_bulleted_list():
    text = "- Mother\n- Father\n- Sister\n- Brother"
    items, raw = parse_free_list(text, truncation_k=25)
    assert items == ["mother", "father", "sister", "brother"]


def test_parse_mixed_case_punctuation():
    text = "1. MOTHER,\n2. Father.\n3. sister!\n4. BROTHER;"
    items, raw = parse_free_list(text, truncation_k=25)
    assert items == ["mother", "father", "sister", "brother"]


def test_parse_deduplication():
    text = "1. Mother\n2. Father\n3. mother\n4. Sister\n5. MOTHER"
    items, raw = parse_free_list(text, truncation_k=25)
    assert items == ["mother", "father", "sister"]
    assert len(raw) == 5  # raw_order keeps all occurrences


def test_parse_truncation():
    lines = [f"{i+1}. item{i}" for i in range(50)]
    text = "\n".join(lines)
    items, raw = parse_free_list(text, truncation_k=10)
    assert len(items) == 10
    assert len(raw) == 50


def test_parse_empty_lines():
    text = "1. Mother\n\n\n2. Father\n\n3. Sister"
    items, raw = parse_free_list(text, truncation_k=25)
    assert items == ["mother", "father", "sister"]


def test_parse_whitespace_collapse():
    text = "1.  Mother   in   law\n2.  Father  in   law"
    items, raw = parse_free_list(text, truncation_k=25)
    assert items == ["mother in law", "father in law"]


def test_parse_fixture_file():
    text = (_FIXTURES / "free_list_response.txt").read_text()
    items, raw = parse_free_list(text, truncation_k=25)

    assert len(items) == 25  # Truncated from 30
    assert len(raw) == 30
    assert items[0] == "mother"
    assert items[1] == "father"
    assert "second cousin" not in items  # Truncated beyond k=25


def test_parse_star_bullet():
    text = "* Mother\n* Father\n* Sister"
    items, raw = parse_free_list(text, truncation_k=25)
    assert items == ["mother", "father", "sister"]


def test_parse_paren_numbering():
    text = "1) Mother\n2) Father\n3) Sister"
    items, raw = parse_free_list(text, truncation_k=25)
    assert items == ["mother", "father", "sister"]
