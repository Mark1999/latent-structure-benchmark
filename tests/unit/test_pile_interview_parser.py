"""Tests for the pile interview parser."""

from pathlib import Path

import pytest
from cdb_collect.protocol.pile_interview import load_prompt, parse_pile_interview

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def test_parse_numbered_labels():
    text = "1. Nuclear family\n2. Extended family\n3. In-laws"
    labels = parse_pile_interview(text, expected_count=3)
    assert labels == ["Nuclear family", "Extended family", "In-laws"]


def test_parse_bulleted_labels():
    text = "- Nuclear family\n- Extended family\n- In-laws"
    labels = parse_pile_interview(text, expected_count=3)
    assert labels == ["Nuclear family", "Extended family", "In-laws"]


def test_parse_with_group_prefix():
    text = "Group 1: Nuclear family\nGroup 2: Extended family"
    labels = parse_pile_interview(text, expected_count=2)
    assert labels == ["Nuclear family", "Extended family"]


def test_parse_quoted_labels():
    text = '1. "Nuclear family"\n2. "Extended family"'
    labels = parse_pile_interview(text, expected_count=2)
    assert labels == ["Nuclear family", "Extended family"]


def test_parse_count_mismatch_raises():
    text = "1. Nuclear family\n2. Extended family"
    with pytest.raises(ValueError, match="Expected 3 labels, got 2"):
        parse_pile_interview(text, expected_count=3)


def test_parse_empty_lines_ignored():
    text = "1. Nuclear family\n\n2. Extended family\n\n3. In-laws"
    labels = parse_pile_interview(text, expected_count=3)
    assert len(labels) == 3


def test_parse_fixture_file():
    text = (_FIXTURES / "pile_interview_response.txt").read_text()
    labels = parse_pile_interview(text, expected_count=8)
    assert len(labels) == 8
    assert labels[0] == "Nuclear family"
    assert labels[7] == "Half-siblings"


def test_load_prompt_formats_piles():
    piles = [["mother", "father"], ["aunt", "uncle"]]
    prompt = load_prompt(piles)
    assert "Group 1: mother, father" in prompt
    assert "Group 2: aunt, uncle" in prompt
