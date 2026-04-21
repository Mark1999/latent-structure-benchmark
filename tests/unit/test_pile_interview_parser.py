"""Tests for the pile interview parser."""

from pathlib import Path

from cdb_collect.protocol.pile_interview import load_prompt, parse_pile_interview

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def test_parse_numbered_labels():
    text = "1. Nuclear family\n2. Extended family\n3. In-laws"
    result = parse_pile_interview(text, expected_count=3)
    assert result.labels == ["Nuclear family", "Extended family", "In-laws"]
    assert result.label_count_mismatch is None


def test_parse_bulleted_labels():
    text = "- Nuclear family\n- Extended family\n- In-laws"
    result = parse_pile_interview(text, expected_count=3)
    assert result.labels == ["Nuclear family", "Extended family", "In-laws"]
    assert result.label_count_mismatch is None


def test_parse_with_group_prefix():
    text = "Group 1: Nuclear family\nGroup 2: Extended family"
    result = parse_pile_interview(text, expected_count=2)
    assert result.labels == ["Nuclear family", "Extended family"]
    assert result.label_count_mismatch is None


def test_parse_quoted_labels():
    text = '1. "Nuclear family"\n2. "Extended family"'
    result = parse_pile_interview(text, expected_count=2)
    assert result.labels == ["Nuclear family", "Extended family"]
    assert result.label_count_mismatch is None


def test_parse_count_mismatch_no_longer_raises():
    """Parser no longer raises on count mismatch — returns structured result.

    CDA SME option (b) FAIL-and-record: the mismatch is surfaced as a
    signal, not an exception. The caller detects it via label_count_mismatch
    and check_8_label_count_match marks the assembled record qa_passed=False.
    See docs/status/2026-04-20-f2-cda-sme-verdict.md §T09.
    """
    text = "1. Nuclear family\n2. Extended family"
    result = parse_pile_interview(text, expected_count=3)
    assert result.label_count_mismatch == (3, 2)
    assert result.labels == ["Nuclear family", "Extended family"]


def test_parse_empty_lines_ignored():
    text = "1. Nuclear family\n\n2. Extended family\n\n3. In-laws"
    result = parse_pile_interview(text, expected_count=3)
    assert len(result.labels) == 3
    assert result.label_count_mismatch is None


def test_parse_fixture_file():
    text = (_FIXTURES / "pile_interview_response.txt").read_text()
    result = parse_pile_interview(text, expected_count=8)
    assert len(result.labels) == 8
    assert result.labels[0] == "Nuclear family"
    assert result.labels[7] == "Half-siblings"
    assert result.label_count_mismatch is None


def test_parse_strips_chatty_postamble():
    """Chatty model postamble should be filtered out."""
    text = (
        "1. Nuclear family\n"
        "2. Extended family\n"
        "3. In-laws\n"
        "Let me know if you'd like me to adjust any of these!"
    )
    result = parse_pile_interview(text, expected_count=3)
    assert result.labels == ["Nuclear family", "Extended family", "In-laws"]
    assert result.label_count_mismatch is None


def test_parse_strips_preamble():
    """Preamble lines should be filtered out."""
    text = (
        "Here are the labels for each group:\n"
        "1. Nuclear family\n"
        "2. Extended family\n"
    )
    result = parse_pile_interview(text, expected_count=2)
    assert result.labels == ["Nuclear family", "Extended family"]
    assert result.label_count_mismatch is None


def test_load_prompt_formats_piles():
    piles = [["mother", "father"], ["aunt", "uncle"]]
    prompt = load_prompt(piles)
    assert "Group 1: mother, father" in prompt
    assert "Group 2: aunt, uncle" in prompt
