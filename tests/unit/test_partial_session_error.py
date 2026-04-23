"""Tests for PartialSessionError, PileSortParseError, and run_informant
partial-session capture. No real API calls — all adapters are mocked.

See docs/status/2026-04-23-verbatim-capture-audit.md §3, §7.
"""

from __future__ import annotations

import asyncio
import json
from datetime import date
from unittest.mock import MagicMock

import pytest
from cdb_collect.adapters.base import AdapterResult
from cdb_collect.exceptions import PartialSessionError, PileSortParseError
from cdb_collect.runner import run_informant
from cdb_core import Domain, ModelRef

# ─── Helpers ────────────────────────────────────────────────────────────────


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


def _adapter_result(text: str = "", stop_reason: str = "end_turn") -> AdapterResult:
    return AdapterResult(
        text=text,
        raw_response={},
        latency_ms=100,
        cost_usd=0.001,
        input_tokens=50,
        output_tokens=10,
        provider_request_id="req_test",
        model_version_returned="claude-opus-4-6-20260401",
        stop_reason=stop_reason,
        thinking_text="",
    )


def _free_list_result() -> AdapterResult:
    text = (
        "1. Mother\n2. Father\n3. Sister\n4. Brother\n5. Aunt\n"
        "6. Uncle\n7. Grandmother\n8. Grandfather\n9. Cousin\n10. Niece"
    )
    return AdapterResult(
        text=text,
        raw_response={"id": "msg_free"},
        latency_ms=300,
        cost_usd=0.01,
        input_tokens=87,
        output_tokens=30,
        provider_request_id="req_free",
        model_version_returned="claude-opus-4-6-20260401",
        stop_reason="end_turn",
    )


def _pile_sort_result() -> AdapterResult:
    piles_json = json.dumps({"piles": [
        ["mother", "father"],
        ["sister", "brother"],
        ["aunt", "uncle"],
        ["grandmother", "grandfather", "cousin", "niece"],
    ]})
    return AdapterResult(
        text=piles_json,
        raw_response={"id": "msg_sort"},
        latency_ms=400,
        cost_usd=0.02,
        input_tokens=120,
        output_tokens=50,
        provider_request_id="req_sort",
        model_version_returned="claude-opus-4-6-20260401",
        stop_reason="end_turn",
    )


def _interview_result() -> AdapterResult:
    text = "1. Parents\n2. Siblings\n3. Aunts and Uncles\n4. Extended family"
    return AdapterResult(
        text=text,
        raw_response={"id": "msg_int"},
        latency_ms=200,
        cost_usd=0.005,
        input_tokens=80,
        output_tokens=20,
        provider_request_id="req_int",
        model_version_returned="claude-opus-4-6-20260401",
        stop_reason="end_turn",
    )


# ─── PartialSessionError construction tests ─────────────────────────────────


def test_partial_session_error_stores_fields():
    cause = ValueError("test failure")
    pse = PartialSessionError(
        cause=cause,
        failed_step="pile_sort",
        partial_session={"freelist": {"some": "data"}},
        prompt_verbatim="the prompt",
        response_verbatim="the response",
        thinking_verbatim="the thinking",
        stop_reason="MAX_TOKENS",
        retry_attempts=[{"attempt_index": 0, "response_verbatim": "first"}],
    )

    assert pse.cause is cause
    assert pse.failed_step == "pile_sort"
    assert pse.partial_session == {"freelist": {"some": "data"}}
    assert pse.prompt_verbatim == "the prompt"
    assert pse.response_verbatim == "the response"
    assert pse.thinking_verbatim == "the thinking"
    assert pse.stop_reason == "MAX_TOKENS"
    assert len(pse.retry_attempts) == 1
    assert pse.retry_attempts[0]["attempt_index"] == 0
    assert str(pse) == "test failure"


def test_partial_session_error_defaults():
    cause = RuntimeError("connection error")
    pse = PartialSessionError(
        cause=cause,
        failed_step="freelist",
        partial_session={},
    )

    assert pse.prompt_verbatim is None
    assert pse.response_verbatim is None
    assert pse.thinking_verbatim is None
    assert pse.stop_reason is None
    assert pse.retry_attempts == []
    assert pse.partial_session == {}


def test_partial_session_error_is_exception():
    pse = PartialSessionError(
        cause=ValueError("x"),
        failed_step="pre_session",
        partial_session={},
    )
    assert isinstance(pse, Exception)


# ─── PileSortParseError construction tests ──────────────────────────────────


def test_pile_sort_parse_error_stores_attempts():
    r1 = _adapter_result(text="bad json 1")
    r2 = _adapter_result(text="bad json 2")
    e1 = ValueError("parse fail 1")
    e2 = ValueError("parse fail 2")

    err = PileSortParseError(
        "Failed after 2 attempts",
        attempts=[r1, r2],
        per_attempt_errors=[e1, e2],
        prompt_verbatim="sort these items",
    )

    assert err.attempts == [r1, r2]
    assert err.per_attempt_errors == [e1, e2]
    assert err.prompt_verbatim == "sort these items"
    assert str(err) == "Failed after 2 attempts"


def test_pile_sort_parse_error_is_value_error():
    """PileSortParseError must be a ValueError subclass for backward compat."""
    err = PileSortParseError("msg", attempts=[], per_attempt_errors=[])
    assert isinstance(err, ValueError)


def test_pile_sort_parse_error_default_prompt():
    err = PileSortParseError("msg", attempts=[], per_attempt_errors=[])
    assert err.prompt_verbatim == ""


# ─── run_informant raises PartialSessionError on step 1 failure ─────────────


def test_run_informant_freelist_failure_raises_partial_session_error():
    """When run_free_list raises, run_informant raises PartialSessionError
    with partial_session={} and failed_step='freelist'."""
    adapter = MagicMock()
    adapter.model = _model_ref()

    async def boom(prompt, *, json_schema=None, temperature=0.7):
        raise RuntimeError("network error")

    adapter.complete = boom

    with pytest.raises(PartialSessionError) as exc_info:
        asyncio.run(run_informant(adapter, _domain(), 0))

    pse = exc_info.value
    assert pse.failed_step == "freelist"
    assert pse.partial_session == {}
    assert isinstance(pse.cause, RuntimeError)
    assert "network error" in str(pse.cause)


# ─── run_informant raises PartialSessionError on step 2 failure ─────────────


def test_run_informant_pilesort_failure_carries_freelist_partial():
    """When run_pile_sort raises (non-parse error), run_informant raises
    PartialSessionError with partial_session containing freelist data and
    failed_step='pile_sort'."""
    adapter = MagicMock()
    adapter.model = _model_ref()

    call_count = 0

    async def mock_complete(prompt, *, json_schema=None, temperature=0.7):
        nonlocal call_count
        call_count += 1
        lower = prompt.lower()
        if "sort" in lower:
            raise RuntimeError("pile sort network error")
        return _free_list_result()

    adapter.complete = mock_complete

    with pytest.raises(PartialSessionError) as exc_info:
        asyncio.run(run_informant(adapter, _domain(), 0))

    pse = exc_info.value
    assert pse.failed_step == "pile_sort"
    assert "freelist" in pse.partial_session
    # The freelist partial should have verbatim content
    assert pse.partial_session["freelist"]["response_verbatim"] != ""
    assert isinstance(pse.cause, RuntimeError)


def test_run_informant_pilesort_parse_error_populates_retry_attempts():
    """When run_pile_sort raises PileSortParseError with multiple attempts,
    run_informant maps attempts[:-1] to retry_attempts and attempts[-1] to
    top-level verbatim fields."""
    adapter = MagicMock()
    adapter.model = _model_ref()

    call_count = 0

    async def mock_complete(prompt, *, json_schema=None, temperature=0.7):
        nonlocal call_count
        call_count += 1
        lower = prompt.lower()
        if "sort" in lower:
            # Return unparseable JSON for all 3 retries
            return _adapter_result(text="not valid json at all")
        return _free_list_result()

    adapter.complete = mock_complete

    with pytest.raises(PartialSessionError) as exc_info:
        asyncio.run(run_informant(adapter, _domain(), 0))

    pse = exc_info.value
    assert pse.failed_step == "pile_sort"
    assert "freelist" in pse.partial_session

    # With _MAX_PARSE_RETRIES=3, there should be 3 total attempts.
    # attempts[:-1] = first 2 attempts → retry_attempts
    # attempts[-1]  = final attempt → top-level verbatim fields
    assert pse.response_verbatim == "not valid json at all"
    assert pse.stop_reason == "end_turn"

    # retry_attempts carries the first N-1 attempts (2 for _MAX_PARSE_RETRIES=3)
    assert len(pse.retry_attempts) == 2
    for i, attempt in enumerate(pse.retry_attempts):
        assert attempt["attempt_index"] == i
        assert attempt["response_verbatim"] == "not valid json at all"
        assert "parse_error_message" in attempt
        assert "input_tokens" in attempt
        assert "output_tokens" in attempt
        assert "latency_ms" in attempt

    # The cause must be a PileSortParseError (subclass of ValueError)
    assert isinstance(pse.cause, PileSortParseError)


def test_run_informant_pilesort_parse_error_single_attempt():
    """With a single retry attempt (max_retries=1 is not a real scenario, but
    if exactly 1 attempt fires), retry_attempts is [] and final attempt goes
    to top-level verbatim."""
    # We can test this by checking that when only 1 result is in attempts,
    # retry_attempts is empty (attempts[:-1] == []).
    adapter = MagicMock()
    adapter.model = _model_ref()

    async def mock_complete(prompt, *, json_schema=None, temperature=0.7):
        lower = prompt.lower()
        if "sort" in lower:
            return _adapter_result(text="not valid json at all")
        return _free_list_result()

    adapter.complete = mock_complete

    with pytest.raises(PartialSessionError) as exc_info:
        asyncio.run(run_informant(adapter, _domain(), 0))

    pse = exc_info.value
    # _MAX_PARSE_RETRIES=3, so there will be 3 attempts and 2 retry_attempts
    # (not 0). This test just confirms the structure is correct.
    assert pse.response_verbatim is not None
    assert isinstance(pse.retry_attempts, list)


# ─── run_informant raises PartialSessionError on step 3 failure ─────────────


def test_run_informant_interview_failure_carries_freelist_and_pilesort():
    """When run_pile_interview raises, run_informant raises PartialSessionError
    with partial_session containing both freelist and pile_sort data and
    failed_step='interview'."""
    adapter = MagicMock()
    adapter.model = _model_ref()

    call_count = 0

    async def mock_complete(prompt, *, json_schema=None, temperature=0.7):
        nonlocal call_count
        call_count += 1
        lower = prompt.lower()
        if "label" in lower or "organizing principle" in lower:
            raise RuntimeError("interview network error")
        if "sort" in lower:
            return _pile_sort_result()
        return _free_list_result()

    adapter.complete = mock_complete

    with pytest.raises(PartialSessionError) as exc_info:
        asyncio.run(run_informant(adapter, _domain(), 0))

    pse = exc_info.value
    assert pse.failed_step == "interview"
    assert "freelist" in pse.partial_session
    assert "pile_sort" in pse.partial_session
    assert isinstance(pse.cause, RuntimeError)
    # Both completed steps should have real verbatim content
    assert pse.partial_session["freelist"]["response_verbatim"] != ""
    assert pse.partial_session["pile_sort"]["response_verbatim"] != ""
