"""Tests for _REASONING_CLASS_NOTE in runner._assemble_record (T3).

CDA SME 2026-07-10 N3: when any step has thoughts_token_count > 0 the
verbatim N3 disclosure text must appear in InformantRecord.capacity_note.

No real API calls. All tests exercise _assemble_record directly.
"""

from __future__ import annotations

from pathlib import Path

from cdb_collect.adapters.base import AdapterResult
from cdb_collect.runner import _REASONING_CLASS_NOTE, _assemble_record
from cdb_core import Domain, FreelistRecord, InterviewRecord, PileSortRecord

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
sys_path_prepend = str(Path(__file__).resolve().parents[2])

# Verbatim text the CDA SME verdict specifies (copy for assertion).
_EXPECTED_NOTE = (
    "Reasoning-class informant: provider records reasoning tokens "
    "(thoughts_token_count) separately from visible output tokens, and "
    "per-step inference latency reflects inference-time reasoning. QA Check 5 "
    "latency ceiling is class-conditioned to 600s and QA Check 6 token "
    "consistency is computed on visible tokens (output_tokens minus "
    "thoughts_token_count) for this record."
)


# ── Helpers ────────────────────────────────────────────────────────────────


def _mock_adapter() -> object:
    """Return a minimal mock that satisfies ModelAdapter's .model attribute."""
    import sys
    sys.path.insert(0, str(_FIXTURES))
    from mock_adapter import MockAdapter
    return MockAdapter(model_id="test/reasoning-model")


def _domain() -> Domain:
    return Domain(
        slug="family",
        version="v1",
        display_name="Family Terms",
        prompt_seed="family relationship",
        truncation_k=10,
    )


def _freelist_rec(thoughts: int = 0, latency_ms: int = 5000) -> FreelistRecord:
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
        latency_ms=latency_ms,
        stop_reason="end_turn",
        parsed_items=items,
        parsed_raw_order=items,
    )


def _pilesort_placeholder() -> PileSortRecord:
    return PileSortRecord(
        prompt_verbatim="",
        prompt_version="v1",
        response_verbatim="",
        response_object_json={},
        input_tokens=0,
        output_tokens=0,
        thoughts_token_count=0,
        latency_ms=0,
        stop_reason="not_collected",
        parsed_piles=[],
        parsed_matrix=[],
        item_source="own_freelist",
    )


def _interview_placeholder() -> InterviewRecord:
    return InterviewRecord(
        prompt_verbatim="",
        prompt_version="v1",
        response_verbatim="",
        response_object_json={},
        input_tokens=0,
        output_tokens=0,
        thoughts_token_count=0,
        latency_ms=0,
        stop_reason="not_collected",
        parsed_pile_labels=[],
    )


def _freelist_result(forced_default_note: str = "") -> AdapterResult:
    return AdapterResult(
        text="test response",
        raw_response={},
        latency_ms=5000,
        input_tokens=50,
        output_tokens=40,
        provider_request_id="req-test-001",
        model_version_returned="test/reasoning-model-v1",
        stop_reason="end_turn",
        forced_default_note=forced_default_note,
    )


def _call_assemble(
    fl: FreelistRecord | None = None,
    ps: PileSortRecord | None = None,
    iv: InterviewRecord | None = None,
    fl_result: AdapterResult | None = None,
) -> object:
    adapter = _mock_adapter()
    domain = _domain()
    return _assemble_record(
        adapter=adapter,
        domain=domain,
        run_index=0,
        freelist_record=fl or _freelist_rec(thoughts=0),
        freelist_result=fl_result or _freelist_result(),
        pilesort_record=ps or _pilesort_placeholder(),
        interview_record=iv or _interview_placeholder(),
        collection_mode="single_pass",
    )


# ── Tests ──────────────────────────────────────────────────────────────────


def test_reasoning_class_note_constant_verbatim():
    """_REASONING_CLASS_NOTE must match the CDA SME verdict N3 text exactly."""
    assert _REASONING_CLASS_NOTE == _EXPECTED_NOTE


def test_all_zero_thoughts_no_reasoning_note():
    """When all steps have thoughts_token_count == 0, no reasoning note in capacity_note."""
    record = _call_assemble(fl=_freelist_rec(thoughts=0))
    assert _EXPECTED_NOTE not in record.capacity_note


def test_freelist_thoughts_emits_note():
    """thoughts_token_count > 0 on freelist step -> reasoning note in capacity_note."""
    record = _call_assemble(fl=_freelist_rec(thoughts=5000))
    assert _EXPECTED_NOTE in record.capacity_note


def test_pilesort_thoughts_emits_note():
    """thoughts_token_count > 0 on pile_sort step -> reasoning note in capacity_note."""
    ps = PileSortRecord(
        prompt_verbatim="",
        prompt_version="v1",
        response_verbatim="",
        response_object_json={},
        input_tokens=0,
        output_tokens=0,
        thoughts_token_count=3000,  # reasoning on pile_sort
        latency_ms=0,
        stop_reason="not_collected",
        parsed_piles=[],
        parsed_matrix=[],
        item_source="own_freelist",
    )
    record = _call_assemble(fl=_freelist_rec(thoughts=0), ps=ps)
    assert _EXPECTED_NOTE in record.capacity_note


def test_interview_thoughts_emits_note():
    """thoughts_token_count > 0 on interview step -> reasoning note in capacity_note."""
    iv = InterviewRecord(
        prompt_verbatim="",
        prompt_version="v1",
        response_verbatim="",
        response_object_json={},
        input_tokens=0,
        output_tokens=0,
        thoughts_token_count=2000,  # reasoning on interview
        latency_ms=0,
        stop_reason="not_collected",
        parsed_pile_labels=[],
    )
    record = _call_assemble(fl=_freelist_rec(thoughts=0), iv=iv)
    assert _EXPECTED_NOTE in record.capacity_note


def test_forced_default_and_reasoning_note_joined():
    """When both forced_default_note and reasoning-class condition apply,
    both notes appear, '; '-joined, forced-default first, reasoning second."""
    forced_note = "Provider forces temperature to default 1.0."
    fl_result = _freelist_result(forced_default_note=forced_note)
    fl = _freelist_rec(thoughts=5000)
    record = _call_assemble(fl=fl, fl_result=fl_result)
    assert forced_note in record.capacity_note
    assert _EXPECTED_NOTE in record.capacity_note
    # forced_default note appears before reasoning note
    idx_forced = record.capacity_note.index(forced_note)
    idx_reasoning = record.capacity_note.index(_EXPECTED_NOTE)
    assert idx_forced < idx_reasoning
    # joined with "; "
    assert "; " in record.capacity_note
