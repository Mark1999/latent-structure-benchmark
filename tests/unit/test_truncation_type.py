"""Tests for InformantRecord.truncation_type population at assembly time.

Covers F2-T04: truncation_type is None on 100/100 real records (shakedown finding 4).
Two source paths tested:
  - Elbow path: run_two_pass uses find_salience_elbow; records get truncation_type="elbow"
  - Context-window path: adapter stop_reason signals length cap; gets "context_window_exceeded"
  - No-truncation path: single_pass with normal stop_reason; truncation_type stays None
"""

from __future__ import annotations

import asyncio
import json
from datetime import date
from unittest.mock import MagicMock

from cdb_collect.adapters.base import AdapterResult
from cdb_collect.runner import _is_context_window_exceeded, run_informant, run_two_pass
from cdb_core import Domain, ModelRef


# ── Shared fixtures ─────────────────────────────────────────────────────────


def _model_ref() -> ModelRef:
    return ModelRef(
        provider="anthropic",
        model_id="claude-opus-4-6",
        family="claude",
        origin="us",
        open_weights=False,
        collection_method="anthropic_api",
        quantization=None,
        release_date=date(2026, 3, 1),
        version_label="4.6",
    )


def _domain() -> Domain:
    return Domain(
        slug="family",
        version="v1",
        display_name="Family Terms",
        prompt_seed="type of family relationship or family member",
        truncation_k=5,
    )


def _free_list_result(stop_reason: str = "end_turn") -> AdapterResult:
    text = "1. Mother\n2. Father\n3. Sister\n4. Brother\n5. Aunt"
    return AdapterResult(
        text=text,
        raw_response={"id": "msg_free", "content": [{"text": text}]},
        latency_ms=350,
        cost_usd=0.01,
        input_tokens=87,
        output_tokens=30,
        provider_request_id="msg_free_123",
        model_version_returned="claude-opus-4-6-20260401",
        stop_reason=stop_reason,
    )


def _free_list_result_length_stop() -> AdapterResult:
    """Simulates a context-window-exceeded free list (Anthropic: stop_reason='max_tokens')."""
    text = "1. Mother\n2. Father\n3. Sister\n4. Brother\n5. Aunt"
    return AdapterResult(
        text=text,
        raw_response={"id": "msg_free_trunc", "content": [{"text": text}]},
        latency_ms=500,
        cost_usd=0.02,
        input_tokens=87,
        output_tokens=16384,
        provider_request_id="msg_free_trunc_123",
        model_version_returned="claude-opus-4-6-20260401",
        stop_reason="max_tokens",  # Anthropic context-window signal
    )


def _pile_sort_result() -> AdapterResult:
    piles_json = json.dumps({
        "piles": [["mother", "father"], ["sister", "brother"], ["aunt"]],
    })
    return AdapterResult(
        text=piles_json,
        raw_response={"id": "msg_sort", "content": [{"text": piles_json}]},
        latency_ms=400,
        cost_usd=0.02,
        input_tokens=120,
        output_tokens=50,
        provider_request_id="msg_sort_123",
        model_version_returned="claude-opus-4-6-20260401",
        stop_reason="end_turn",
    )


def _interview_result() -> AdapterResult:
    text = "1. Parents\n2. Siblings\n3. Extended family"
    return AdapterResult(
        text=text,
        raw_response={"id": "msg_int", "content": [{"text": text}]},
        latency_ms=200,
        cost_usd=0.005,
        input_tokens=80,
        output_tokens=20,
        provider_request_id="msg_int_123",
        model_version_returned="claude-opus-4-6-20260401",
        stop_reason="end_turn",
    )


def _mock_adapter(freelist_stop_reason: str = "end_turn") -> MagicMock:
    """Mock adapter dispatches responses based on prompt content.

    Args:
        freelist_stop_reason: stop_reason to inject on freelist responses.
            Use "max_tokens" / "length" / "MAX_TOKENS" to simulate context cap.
    """
    adapter = MagicMock()
    adapter.model = _model_ref()

    async def mock_complete(prompt, *, json_schema=None, temperature=0.7):
        lower = prompt.lower()
        if "label" in lower or "organizing principle" in lower:
            return _interview_result()
        elif "sort" in lower:
            return _pile_sort_result()
        else:
            return _free_list_result(stop_reason=freelist_stop_reason)

    adapter.complete = mock_complete
    return adapter


# ── Helper: _is_context_window_exceeded ─────────────────────────────────────


def test_is_context_window_exceeded_anthropic():
    assert _is_context_window_exceeded("max_tokens") is True


def test_is_context_window_exceeded_openai_compat():
    """OpenAI / OpenRouter / HuggingFace / xAI / DeepSeek / Mistral use 'length'."""
    assert _is_context_window_exceeded("length") is True


def test_is_context_window_exceeded_gemini():
    """Google Gemini FinishReason enum name is 'MAX_TOKENS'."""
    assert _is_context_window_exceeded("MAX_TOKENS") is True


def test_is_context_window_exceeded_normal_stop():
    assert _is_context_window_exceeded("end_turn") is False
    assert _is_context_window_exceeded("stop") is False
    assert _is_context_window_exceeded("not_collected") is False
    assert _is_context_window_exceeded("unknown") is False


# ── Elbow path: run_two_pass ─────────────────────────────────────────────────


def test_two_pass_freelist_records_get_elbow_truncation_type():
    """All free-list records from run_two_pass get truncation_type='elbow'."""
    records = asyncio.run(
        run_two_pass(_mock_adapter(), _domain(), n_free_lists=2, n_pile_sorts=1)
    )
    # First 2 records are freelist-only (pass 1)
    for rec in records[:2]:
        assert rec.truncation_type == "elbow", (
            f"Expected 'elbow', got {rec.truncation_type!r} (run_index={rec.run_index})"
        )


def test_two_pass_pile_sort_records_get_elbow_truncation_type():
    """Pile-sort records from run_two_pass get truncation_type='elbow'."""
    records = asyncio.run(
        run_two_pass(_mock_adapter(), _domain(), n_free_lists=2, n_pile_sorts=2)
    )
    # Last 2 records are pile-sort (pass 2)
    for rec in records[2:]:
        assert rec.truncation_type == "elbow", (
            f"Expected 'elbow', got {rec.truncation_type!r} (run_index={rec.run_index})"
        )


def test_two_pass_truncation_n_equals_elbow_k():
    """truncation_n is set to elbow_k (> 0) on all two_pass records."""
    records = asyncio.run(
        run_two_pass(_mock_adapter(), _domain(), n_free_lists=2, n_pile_sorts=1)
    )
    for rec in records:
        assert rec.truncation_n is not None and rec.truncation_n > 0, (
            f"Expected positive truncation_n, got {rec.truncation_n!r}"
        )


# ── Context-window path ──────────────────────────────────────────────────────


def test_single_pass_context_window_exceeded_anthropic():
    """When freelist stop_reason='max_tokens', truncation_type='context_window_exceeded'."""
    adapter = _mock_adapter(freelist_stop_reason="max_tokens")
    record = asyncio.run(run_informant(adapter, _domain(), 0))
    assert record.truncation_type == "context_window_exceeded"
    assert record.context_window_exceeded is True


def test_single_pass_context_window_exceeded_openai_compat():
    """When freelist stop_reason='length' (OpenAI-compat), truncation_type='context_window_exceeded'."""
    adapter = _mock_adapter(freelist_stop_reason="length")
    record = asyncio.run(run_informant(adapter, _domain(), 0))
    assert record.truncation_type == "context_window_exceeded"
    assert record.context_window_exceeded is True


def test_single_pass_context_window_exceeded_gemini():
    """When freelist stop_reason='MAX_TOKENS' (Gemini), truncation_type='context_window_exceeded'."""
    adapter = _mock_adapter(freelist_stop_reason="MAX_TOKENS")
    record = asyncio.run(run_informant(adapter, _domain(), 0))
    assert record.truncation_type == "context_window_exceeded"
    assert record.context_window_exceeded is True


def test_context_window_exceeded_sets_capacity_note():
    """capacity_note names the affected step when context window is exceeded."""
    adapter = _mock_adapter(freelist_stop_reason="max_tokens")
    record = asyncio.run(run_informant(adapter, _domain(), 0))
    assert "freelist" in record.capacity_note


def test_two_pass_freelist_context_window_preserved_over_elbow():
    """If a freelist response hit context window, that label is kept (not overwritten by 'elbow')."""
    adapter = _mock_adapter(freelist_stop_reason="max_tokens")
    records = asyncio.run(
        run_two_pass(adapter, _domain(), n_free_lists=2, n_pile_sorts=1)
    )
    # Freelist-only records (pass 1) should have "context_window_exceeded"
    for rec in records[:2]:
        assert rec.truncation_type == "context_window_exceeded", (
            f"Expected 'context_window_exceeded', got {rec.truncation_type!r}"
        )
    # Pile-sort records (pass 2) do not have freelist — should still get "elbow"
    for rec in records[2:]:
        assert rec.truncation_type == "elbow", (
            f"Expected 'elbow' on pile-sort record, got {rec.truncation_type!r}"
        )


# ── No-truncation (normal) path ──────────────────────────────────────────────


def test_single_pass_no_truncation_gives_none():
    """Single-pass record with normal stop_reason has truncation_type=None.

    single_pass does not apply find_salience_elbow — the model sorts its own
    free list in full. No elbow truncation occurs, so truncation_type stays None.
    """
    record = asyncio.run(run_informant(_mock_adapter(), _domain(), 0))
    assert record.truncation_type is None
    assert record.context_window_exceeded is False
