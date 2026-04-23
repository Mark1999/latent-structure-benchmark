"""Tests for the deterministic decline-detection module.

Coverage per CDA SME verdict 2026-04-23 §1.3 triggers (a)–(e).
No real API calls.
"""

from __future__ import annotations

import pytest
from cdb_collect.decline_detection import (
    DECLINE_ALLOWLIST_VERSION,
    _matches_allowlist,
    detect_all,
    detect_from_failure,
    detect_from_informant,
)

# ── Helpers ───────────────────────────────────────────────────────────────

def _make_informant(
    *,
    qa_passed: bool = False,
    informant_id: str = "abc123",
    parsed_piles: list | None = None,
    pile_response: str = "Sorted piles above.",
    parsed_items: list | None = None,
    parsed_labels: list | None = None,
    interview_response: str = "",
) -> dict:
    """Build a minimal informants.jsonl-shaped dict for testing."""
    if parsed_piles is None:
        parsed_piles = [["mother", "father"], ["sister", "brother"]]
    if parsed_items is None:
        parsed_items = ["mother", "father", "sister", "brother"]
    if parsed_labels is None:
        parsed_labels = ["parents", "siblings"]

    return {
        "informant_id": informant_id,
        "qa_passed": qa_passed,
        "freelist": {
            "parsed_items": parsed_items,
            "response_verbatim": "1. mother\n2. father\n3. sister\n4. brother",
        },
        "pile_sort": {
            "parsed_piles": parsed_piles,
            "response_verbatim": pile_response,
        },
        "interview": {
            "parsed_pile_labels": parsed_labels,
            "response_verbatim": interview_response,
        },
    }


def _make_failure(
    *,
    error_type: str = "ValueError",
    model_id: str = "gpt-4o",
    domain: str = "family",
    run_index: int = 0,
    timestamp: str = "2026-04-23T10:00:00",
) -> dict:
    return {
        "timestamp": timestamp,
        "error_type": error_type,
        "error_message": "some error",
        "context": {
            "model_id": model_id,
            "domain": domain,
            "run_index": run_index,
        },
        "retry_attempts": [],
    }


# ── DECLINE_ALLOWLIST_VERSION constant ────────────────────────────────────

def test_allowlist_version_constant():
    """DECLINE_ALLOWLIST_VERSION must be the frozen string 'v1'."""
    assert DECLINE_ALLOWLIST_VERSION == "v1"


# ── Allowlist matching ─────────────────────────────────────────────────────

@pytest.mark.parametrize("phrase,text", [
    ("I can't", "I can't do that."),
    ("I cannot", "I cannot complete this task."),
    ("I'm not able", "I'm not able to assist."),
    ("I am unable", "I am unable to help."),
    ("I won't", "I won't do this."),
    ("I decline", "I decline the request."),
    ("I refuse", "I refuse to answer."),
    ("I'm sorry, but", "I'm sorry, but I can't help."),
    ("I apologize, but", "I apologize, but that's not something I can do."),
    ("As an AI", "As an AI I don't have that capability."),
    ("I'm not comfortable", "I'm not comfortable with this task."),
    ("against my", "That goes against my guidelines."),
    ("violates", "This request violates my usage policy."),
    ("I must decline", "I must decline to proceed."),
])
def test_allowlist_match_positive(phrase: str, text: str):
    """Each allowlist phrase must match in a representative sentence."""
    assert _matches_allowlist(text), f"Expected match for phrase: {phrase!r}"


@pytest.mark.parametrize("text", [
    "Sure, here are some family terms: mother, father, sister.",
    "1. Mother\n2. Father\n3. Sister",
    "The items sort naturally into two groups.",
    "",
])
def test_allowlist_match_negative(text: str):
    """Non-refusal text must not match the allowlist."""
    assert not _matches_allowlist(text)


def test_allowlist_case_insensitive():
    """Allowlist matching is case-insensitive."""
    assert _matches_allowlist("I CAN'T do that.")
    assert _matches_allowlist("i cannot process this")
    assert _matches_allowlist("AS AN AI language model")


# ── Trigger (a): pile-sort 0 piles ────────────────────────────────────────

def test_trigger_a_empty_piles():
    """Trigger (a): pile-sort parsed_piles empty → empty_output on pile_sort."""
    rec = _make_informant(parsed_piles=[])
    result = detect_from_informant(rec)
    assert result is not None
    assert result.originating_outcome_class == "empty_output"
    assert result.originating_step == "pile_sort"
    assert result.source == "informants"
    assert result.identifier == "abc123"


# ── Trigger (b): pile-sort response matches allowlist ─────────────────────

def test_trigger_b_refusal_string():
    """Trigger (b): pile-sort response contains allowlist phrase → refusal_string_match."""
    rec = _make_informant(
        pile_response="I cannot sort these items for you.",
        # Give it non-empty piles so trigger (a) doesn't fire first
        parsed_piles=[["mother"], ["father"]],
    )
    # Trigger (b) fires only when piles are non-empty (a didn't fire)
    result = detect_from_informant(rec)
    assert result is not None
    assert result.originating_outcome_class == "refusal_string_match"
    assert result.originating_step == "pile_sort"


def test_trigger_b_apology_framed():
    """Trigger (b): apology-framed RLHF pattern → refusal_string_match."""
    rec = _make_informant(
        pile_response="I'm sorry, but I can't help with sorting tasks.",
        parsed_piles=[["mother"], ["father"]],
    )
    result = detect_from_informant(rec)
    assert result is not None
    assert result.originating_outcome_class == "refusal_string_match"


def test_trigger_b_as_an_ai():
    """Trigger (b): 'As an AI' pattern → refusal_string_match."""
    rec = _make_informant(
        pile_response="As an AI, I don't sort items.",
        parsed_piles=[["mother"], ["father"]],
    )
    result = detect_from_informant(rec)
    assert result is not None
    assert result.originating_outcome_class == "refusal_string_match"


# ── Trigger (c): free-list 0 items ────────────────────────────────────────

def test_trigger_c_empty_freelist():
    """Trigger (c): free-list parsed_items empty → empty_output on freelist."""
    # Piles must be non-empty and clean so (a) and (b) don't fire
    rec = _make_informant(
        parsed_items=[],
        parsed_piles=[["mother"], ["father"]],
        pile_response="Here are the piles.",
    )
    result = detect_from_informant(rec)
    assert result is not None
    assert result.originating_outcome_class == "empty_output"
    assert result.originating_step == "freelist"


# ── Trigger (d): interview 0 labels, non-empty response ───────────────────

def test_trigger_d_empty_labels_nonempty_response():
    """Trigger (d): interview returns text but no parsed labels → empty_output."""
    rec = _make_informant(
        parsed_labels=[],
        interview_response="I organized the items by kinship.",
        # Keep piles and freelist clean
        parsed_piles=[["mother"], ["father"]],
        parsed_items=["mother", "father"],
        pile_response="Here are the sorted piles.",
    )
    result = detect_from_informant(rec)
    assert result is not None
    assert result.originating_outcome_class == "empty_output"
    assert result.originating_step == "interview"


def test_trigger_d_empty_labels_empty_response_no_fire():
    """Trigger (d) requires non-empty response — does not fire on silent empty."""
    rec = _make_informant(
        parsed_labels=[],
        interview_response="",  # empty → trigger (d) does not apply
        parsed_piles=[["mother"], ["father"]],
        parsed_items=["mother", "father"],
        pile_response="Here are the sorted piles.",
    )
    result = detect_from_informant(rec)
    # No trigger fires (piles non-empty, freelist non-empty, interview response empty)
    assert result is None


# ── Trigger (e): single-degenerate-pile ────────────────────────────────────

def test_trigger_e_single_degenerate_pile():
    """Trigger (e): 1 pile containing ≥ 95% of items → single_degenerate_pile."""
    items = [f"item{i}" for i in range(20)]
    # 19/20 = 0.95 — exactly at threshold
    rec = _make_informant(
        parsed_piles=[items[:19], [items[19]]],
        parsed_items=items,
        pile_response="Sorted.",
    )
    # This is actually 2 piles — trigger (e) fires on exactly 1 pile
    result = detect_from_informant(rec)
    assert result is None  # 2 piles, not 1

    # Now: 1 pile containing all 20 items
    rec_single = _make_informant(
        parsed_piles=[items],  # 1 pile, all 20 items → 20/20 = 1.0 ≥ 0.95
        parsed_items=items,
        pile_response="All in one pile.",
    )
    result_single = detect_from_informant(rec_single)
    assert result_single is not None
    assert result_single.originating_outcome_class == "single_degenerate_pile"
    assert result_single.originating_step == "pile_sort"


def test_trigger_e_single_pile_below_threshold():
    """Single pile but below 0.95 threshold → no trigger (e)."""
    items = [f"item{i}" for i in range(20)]
    # 1 pile with 18/20 = 0.90 < 0.95
    rec = _make_informant(
        parsed_piles=[items[:18]],  # 18 items in 1 pile, total 20
        parsed_items=items,
        pile_response="One pile.",
    )
    result = detect_from_informant(rec)
    # Trigger (a) fires because piles list length doesn't matter — but wait:
    # len(parsed_piles) == 1 (non-empty), so trigger (a) doesn't fire.
    # Trigger (b) doesn't fire. Trigger (c) doesn't fire. Trigger (d) doesn't fire.
    # Trigger (e): 18/20 = 0.90 < 0.95 → does not fire.
    # But pile contains only 18 of 20 items... the items_in_single_pile is len of the pile list
    assert result is None


def test_trigger_e_exactly_95_percent():
    """Single pile at exactly 95% (19/20) → trigger (e) fires."""
    items = [f"item{i}" for i in range(20)]
    rec = _make_informant(
        parsed_piles=[items[:19]],  # 1 pile, 19 items, total freelist 20 → 0.95
        parsed_items=items,
        pile_response="One pile.",
    )
    result = detect_from_informant(rec)
    assert result is not None
    assert result.originating_outcome_class == "single_degenerate_pile"


# ── qa_passed=True records are skipped ────────────────────────────────────

def test_qa_passed_skipped():
    """qa_passed=True records are never flagged (triggers only fire on qa_passed=False)."""
    rec = _make_informant(qa_passed=True, parsed_piles=[])
    result = detect_from_informant(rec)
    assert result is None


# ── Failure detection ──────────────────────────────────────────────────────

def test_detect_from_failure_basic():
    """Any failure entry produces a DetectedSession."""
    entry = _make_failure()
    result = detect_from_failure(entry)
    assert result is not None
    assert result.source == "failures"
    assert result.originating_outcome_class in (
        "http_error", "timeout", "parse_failure", "other"
    )


def test_detect_from_failure_http_error():
    """HTTP error class maps to http_error outcome."""
    entry = _make_failure(error_type="httpx.HTTPStatusError")
    result = detect_from_failure(entry)
    assert result is not None
    assert result.originating_outcome_class == "http_error"


def test_detect_from_failure_timeout():
    """Timeout class maps to timeout outcome."""
    entry = _make_failure(error_type="TimeoutError")
    result = detect_from_failure(entry)
    assert result is not None
    assert result.originating_outcome_class == "timeout"


def test_detect_from_failure_parse():
    """Parse/value error class maps to parse_failure outcome."""
    entry = _make_failure(error_type="PileSortParseError")
    result = detect_from_failure(entry)
    assert result is not None
    assert result.originating_outcome_class == "parse_failure"


def test_detect_from_failure_identifier_is_stable():
    """Same failure entry always produces the same identifier."""
    entry = _make_failure(model_id="gpt-4o", domain="family", run_index=0)
    r1 = detect_from_failure(entry)
    r2 = detect_from_failure(entry)
    assert r1 is not None and r2 is not None
    assert r1.identifier == r2.identifier


# ── detect_all combines both sources ──────────────────────────────────────

def test_detect_all_empty_inputs():
    """detect_all on empty lists returns empty list."""
    assert detect_all([], []) == []


def test_detect_all_combines():
    """detect_all combines informant triggers and failure triggers."""
    bad_rec = _make_informant(parsed_piles=[])
    good_rec = _make_informant(qa_passed=True)
    failure = _make_failure()

    results = detect_all([bad_rec, good_rec], [failure])
    # 1 from informant + 1 from failure
    assert len(results) == 2
    sources = [r.source for r in results]
    assert "informants" in sources
    assert "failures" in sources


def test_detect_all_informants_before_failures():
    """Informant results are returned before failure results (order preserved)."""
    bad_rec = _make_informant(parsed_piles=[])
    failure = _make_failure()
    results = detect_all([bad_rec], [failure])
    assert results[0].source == "informants"
    assert results[1].source == "failures"
