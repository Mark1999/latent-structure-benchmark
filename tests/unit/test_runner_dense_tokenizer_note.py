"""Tests for _DENSE_TOKENIZER_NOTE in runner._assemble_record (T8 N10).

CDA SME 2026-07-10 addendum N10: when adapter.model.model_id is in
DENSE_TOKENIZER_MODEL_IDS, the verbatim N10 disclosure text must appear in
InformantRecord.capacity_note. When both N3 (reasoning) and N10 (dense)
apply, the two notes are separated by two newlines.

No real API calls. All tests exercise _assemble_record directly.
"""

from __future__ import annotations

from pathlib import Path

from cdb_collect.adapters.base import AdapterResult
from cdb_collect.runner import (
    _DENSE_TOKENIZER_MODEL_IDS,
    _DENSE_TOKENIZER_NOTE,
    _REASONING_CLASS_NOTE,
    _assemble_record,
)
from cdb_core import Domain, FreelistRecord, InterviewRecord, PileSortRecord

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"

# Verbatim N10 text from the CDA SME addendum (copy for assertion).
_EXPECTED_DENSE_NOTE = (
    "Dense-tokenizer informant: this model uses a tokenizer producing "
    "approximately 1.7 to 1.85 characters per output token in "
    "campaign-measured freelist output, compared with 2.5 to 2.7 for the "
    "pre-Claude-5 informant cohort. QA Check 6 expected-token arithmetic is "
    "class-conditioned to the denser ratio for this record."
)


# ── Helpers ────────────────────────────────────────────────────────────────


def _mock_adapter(model_id: str) -> object:
    """Return a minimal mock adapter with the given model_id."""
    import sys
    sys.path.insert(0, str(_FIXTURES))
    from mock_adapter import MockAdapter
    return MockAdapter(model_id=model_id)


def _domain() -> Domain:
    return Domain(
        slug="family",
        version="v1",
        display_name="Family Terms",
        prompt_seed="family relationship",
        truncation_k=10,
    )


def _freelist_rec(thoughts: int = 0) -> FreelistRecord:
    items = [f"item{i}" for i in range(15)]
    rv = "1. " + "\n2. ".join(items)
    output_tokens = thoughts + max(1, round(len(rv) / 4))
    return FreelistRecord(
        prompt_verbatim="test",
        prompt_version="v1",
        response_verbatim=rv,
        response_object_json={},
        input_tokens=50,
        output_tokens=output_tokens,
        thoughts_token_count=thoughts,
        latency_ms=5000,
        stop_reason="end_turn",
        parsed_items=items,
        parsed_raw_order=items,
    )


def _pilesort_placeholder() -> PileSortRecord:
    return PileSortRecord(
        prompt_verbatim="", prompt_version="v1", response_verbatim="",
        response_object_json={}, input_tokens=0, output_tokens=0,
        thoughts_token_count=0, latency_ms=0, stop_reason="not_collected",
        parsed_piles=[], parsed_matrix=[], item_source="own_freelist",
    )


def _interview_placeholder() -> InterviewRecord:
    return InterviewRecord(
        prompt_verbatim="", prompt_version="v1", response_verbatim="",
        response_object_json={}, input_tokens=0, output_tokens=0,
        thoughts_token_count=0, latency_ms=0, stop_reason="not_collected",
        parsed_pile_labels=[],
    )


def _freelist_result() -> AdapterResult:
    return AdapterResult(
        text="test", raw_response={}, latency_ms=5000,
        input_tokens=50, output_tokens=40,
        provider_request_id="req-test-001",
        model_version_returned="model-v1", stop_reason="end_turn",
    )


def _call_assemble(model_id: str, fl: FreelistRecord | None = None) -> object:
    adapter = _mock_adapter(model_id)
    return _assemble_record(
        adapter=adapter,
        domain=_domain(),
        run_index=0,
        freelist_record=fl or _freelist_rec(thoughts=0),
        freelist_result=_freelist_result(),
        pilesort_record=_pilesort_placeholder(),
        interview_record=_interview_placeholder(),
        collection_mode="single_pass",
    )


# ── Tests ──────────────────────────────────────────────────────────────────


def test_dense_tokenizer_note_constant_verbatim():
    """_DENSE_TOKENIZER_NOTE must match the CDA SME addendum N10 text exactly."""
    assert _DENSE_TOKENIZER_NOTE == _EXPECTED_DENSE_NOTE


def test_dense_tokenizer_model_ids_mirrored_in_runner():
    """_DENSE_TOKENIZER_MODEL_IDS in runner.py must contain the same bare IDs as qa_check.py."""
    assert "claude-opus-4-8" in _DENSE_TOKENIZER_MODEL_IDS
    assert "claude-sonnet-5" in _DENSE_TOKENIZER_MODEL_IDS


def test_non_dense_model_no_dense_note():
    """A non-dense model must not carry the N10 capacity note."""
    record = _call_assemble("test/non-dense-model")
    assert _EXPECTED_DENSE_NOTE not in record.capacity_note


def test_claude_opus_48_emits_dense_note():
    """claude-opus-4-8 triggers the N10 capacity note."""
    record = _call_assemble("claude-opus-4-8")
    assert _EXPECTED_DENSE_NOTE in record.capacity_note


def test_claude_sonnet_5_emits_dense_note():
    """claude-sonnet-5 triggers the N10 capacity note."""
    record = _call_assemble("claude-sonnet-5")
    assert _EXPECTED_DENSE_NOTE in record.capacity_note


def test_only_dense_no_reasoning_uses_semicolon_join():
    """When only N10 applies (no N3), dense note is joined with '; ' to prior notes."""
    record = _call_assemble("claude-sonnet-5", fl=_freelist_rec(thoughts=0))
    assert _EXPECTED_DENSE_NOTE in record.capacity_note
    # The N3 note must NOT be present.
    assert _REASONING_CLASS_NOTE not in record.capacity_note
    # No double-newline separator (only semicolons expected).
    assert "\n\n" not in record.capacity_note


def test_both_n3_and_n10_separated_by_double_newline():
    """When both N3 (reasoning) and N10 (dense) apply, notes are separated by two newlines.

    The addendum explicitly forbids merging; each disclosure must be
    independently readable.
    """
    # fl with thoughts_token_count > 0 triggers N3; claude-sonnet-5 triggers N10.
    fl = _freelist_rec(thoughts=5000)
    record = _call_assemble("claude-sonnet-5", fl=fl)

    assert _REASONING_CLASS_NOTE in record.capacity_note
    assert _EXPECTED_DENSE_NOTE in record.capacity_note

    # The two notes must be separated by "\n\n", not "; ".
    # Check that "\n\n" appears between the two notes.
    idx_reasoning = record.capacity_note.index(_REASONING_CLASS_NOTE)
    idx_dense = record.capacity_note.index(_EXPECTED_DENSE_NOTE)
    between = record.capacity_note[idx_reasoning + len(_REASONING_CLASS_NOTE):idx_dense]
    assert "\n\n" in between, (
        f"Expected '\\n\\n' between N3 and N10 notes; found separator: {between!r}"
    )
