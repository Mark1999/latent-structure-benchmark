"""Tests for the pile sort parser and binary matrix builder."""

import json
from pathlib import Path

import pytest
from cdb_collect.protocol.pile_sort import (
    build_binary_matrix,
    parse_pile_sort,
)

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"

_ITEMS = ["mother", "father", "sister", "brother", "aunt"]


def test_parse_valid_json():
    text = json.dumps({"piles": [["mother", "father"], ["sister", "brother"], ["aunt"]]})
    piles, matrix = parse_pile_sort(text, _ITEMS)
    assert len(piles) == 3
    assert piles[0] == ["mother", "father"]


def test_parse_markdown_wrapped_json():
    text = '```json\n{"piles": [["mother", "father"], ["sister", "brother", "aunt"]]}\n```'
    piles, matrix = parse_pile_sort(text, _ITEMS)
    assert len(piles) == 2


def test_parse_json_with_surrounding_text():
    text = (
        'Here are the piles:\n'
        '{"piles": [["mother", "father", "sister", "brother", "aunt"]]}\nDone!'
    )
    piles, matrix = parse_pile_sort(text, _ITEMS)
    assert len(piles) == 1
    assert len(piles[0]) == 5


def test_parse_case_insensitive():
    text = json.dumps({"piles": [["Mother", "Father"], ["Sister", "Brother", "Aunt"]]})
    piles, matrix = parse_pile_sort(text, _ITEMS)
    assert len(piles) == 2
    # Items should be normalized to match expected_items
    assert piles[0][0] == "mother"


def test_parse_few_missing_items_tolerated():
    """Up to 10% missing items (min 1) is tolerated."""
    text = json.dumps({"piles": [["mother", "father"], ["sister", "brother"]]})
    piles, matrix = parse_pile_sort(text, _ITEMS)
    assert len(piles) == 2  # aunt missing but tolerated


def test_parse_many_missing_items_raises():
    """More than 10% missing items raises."""
    text = json.dumps({"piles": [["mother"]]})
    with pytest.raises(ValueError, match="missing"):
        parse_pile_sort(text, _ITEMS)


def test_parse_duplicate_item_raises():
    text = json.dumps({
        "piles": [["mother", "father", "mother"], ["sister", "brother", "aunt"]],
    })
    with pytest.raises(ValueError, match="Duplicate"):
        parse_pile_sort(text, _ITEMS)


def test_parse_unexpected_item_skipped():
    """Unexpected items are silently skipped."""
    text = json.dumps({"piles": [["mother", "father", "cousin"], ["sister", "brother", "aunt"]]})
    piles, matrix = parse_pile_sort(text, _ITEMS)
    assert len(piles) == 2
    # "cousin" not in _ITEMS, so it's skipped
    assert piles[0] == ["mother", "father"]
    assert piles[1] == ["sister", "brother", "aunt"]


def test_parse_missing_piles_key():
    text = json.dumps({"groups": [["mother"]]})
    with pytest.raises(ValueError, match="piles"):
        parse_pile_sort(text, _ITEMS)


def test_build_binary_matrix_basic():
    items = ["a", "b", "c"]
    piles = [["a", "b"], ["c"]]
    matrix = build_binary_matrix(piles, items)

    # a and b in same pile
    assert matrix[0][1] == 1
    assert matrix[1][0] == 1
    # a and c in different piles
    assert matrix[0][2] == 0
    assert matrix[2][0] == 0
    # b and c in different piles
    assert matrix[1][2] == 0


def test_build_binary_matrix_diagonal():
    items = ["a", "b", "c"]
    piles = [["a"], ["b"], ["c"]]
    matrix = build_binary_matrix(piles, items)
    for i in range(3):
        assert matrix[i][i] == 1


def test_build_binary_matrix_symmetric():
    items = ["a", "b", "c", "d"]
    piles = [["a", "b", "c"], ["d"]]
    matrix = build_binary_matrix(piles, items)
    n = len(items)
    for i in range(n):
        for j in range(n):
            assert matrix[i][j] == matrix[j][i]


def test_parse_fixture_file():
    fixture = json.loads((_FIXTURES / "pile_sort_response.json").read_text())
    # Collect all items from the fixture
    all_items = []
    for pile in fixture["piles"]:
        all_items.extend(pile)

    text = json.dumps(fixture)
    piles, matrix = parse_pile_sort(text, all_items)
    assert len(piles) == 8
    assert len(matrix) == len(all_items)
    # Verify symmetric
    n = len(matrix)
    for i in range(n):
        for j in range(n):
            assert matrix[i][j] == matrix[j][i]


def test_all_in_one_pile():
    items = ["a", "b", "c"]
    piles = [["a", "b", "c"]]
    matrix = build_binary_matrix(piles, items)
    # All pairs should be 1
    for i in range(3):
        for j in range(3):
            assert matrix[i][j] == 1
