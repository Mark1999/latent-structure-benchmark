"""Tests for QA check script. See ARCHITECTURE.md §4.1.6."""

from __future__ import annotations

from datetime import date, datetime
from unittest.mock import patch

from cdb_core import FreelistRecord, InformantRecord, InterviewRecord, PileSortRecord

# Import the check functions directly
from scripts.qa_check import (
    check_1_freelist_count,
    check_2_freelist_uniqueness,
    check_3_pilesort_binary,
    check_4_pilesort_symmetric,
    check_5_latency,
    check_6_token_consistency,
    check_7_provider_request_id,
    post_to_slack,
    run_qa_checks,
)


def _freelist(items: list[str] | None = None, latency_ms: int = 500) -> FreelistRecord:
    if items is None:
        items = [f"item{i}" for i in range(15)]
    response_text = "1. " + "\n2. ".join(items)
    # Set output_tokens to match response length / 4 (within tolerance)
    output_tokens = max(1, round(len(response_text) / 4))
    return FreelistRecord(
        prompt_verbatim="test prompt",
        prompt_version="v1",
        response_verbatim=response_text,
        response_object_json={},
        input_tokens=50,
        output_tokens=output_tokens,
        latency_ms=latency_ms,
        stop_reason="end_turn",
        parsed_items=items,
        parsed_raw_order=items,
    )


def _pilesort(
    matrix: list[list[int]] | None = None,
    latency_ms: int = 0,
    collected: bool = False,
) -> PileSortRecord:
    return PileSortRecord(
        prompt_verbatim="" if not collected else "test",
        prompt_version="v1",
        response_verbatim="" if not collected else "test",
        response_object_json={},
        input_tokens=0,
        output_tokens=0,
        latency_ms=latency_ms,
        stop_reason="not_collected" if not collected else "end_turn",
        parsed_piles=[],
        parsed_matrix=matrix or [],
    )


def _interview() -> InterviewRecord:
    return InterviewRecord(
        prompt_verbatim="",
        prompt_version="v1",
        response_verbatim="",
        response_object_json={},
        input_tokens=0,
        output_tokens=0,
        latency_ms=0,
        stop_reason="not_collected",
        parsed_pile_labels=[],
    )


def _record(
    freelist: FreelistRecord | None = None,
    pilesort: PileSortRecord | None = None,
    provider_request_id: str = "msg_test123",
    model_id: str = "claude-opus-4-6",
    run_index: int = 0,
) -> InformantRecord:
    return InformantRecord(
        informant_id=f"test_{run_index}",
        domain_slug="family",
        run_index=run_index,
        collection_date=datetime(2026, 4, 13, 10, 0, 0),
        model_id=model_id,
        model_version_returned="claude-opus-4-6-20260401",
        family="claude",
        provider="anthropic",
        provider_request_id=provider_request_id,
        knowledge_cutoff=date(2025, 5, 1),
        open_weights=False,
        origin_country="us",
        alignment_method=None,
        collection_method="anthropic_api",
        api_endpoint="https://api.anthropic.com/v1/messages",
        api_version="2023-06-01",
        temperature=0.7,
        top_p=None,
        max_tokens=4096,
        system_prompt="",
        freelist=freelist or _freelist(),
        pile_sort=pilesort or _pilesort(),
        interview=_interview(),
        sha256_manifest={
            "freelist_prompt": "a" * 64,
            "freelist_response": "b" * 64,
            "pilesort_prompt": "c" * 64,
            "pilesort_response": "d" * 64,
            "interview_prompt": "e" * 64,
            "interview_response": "f" * 64,
            "request_params": "0" * 64,
            "informant_record_total": "1" * 64,
        },
        qa_passed=True,
        qa_notes="",
    )


# ─── Check 1: Free-list item count ──────────────────────────────────

def test_check1_pass():
    record = _record(freelist=_freelist(items=[f"i{i}" for i in range(10)]))
    assert check_1_freelist_count(record) is None


def test_check1_fail():
    record = _record(freelist=_freelist(items=[f"i{i}" for i in range(9)]))
    failure = check_1_freelist_count(record)
    assert failure is not None
    assert failure.check_num == 1


# ─── Check 2: Cross-run uniqueness ──────────────────────────────────

def test_check2_single_run_passes():
    record = _record()
    assert check_2_freelist_uniqueness(record, [record]) is None


def test_check2_diverse_runs_pass():
    r1 = _record(
        freelist=_freelist(items=[f"a{i}" for i in range(10)]),
        run_index=0,
    )
    r2 = _record(
        freelist=_freelist(items=[f"b{i}" for i in range(10)]),
        run_index=1,
    )
    assert check_2_freelist_uniqueness(r1, [r1, r2]) is None


def test_check2_identical_runs_fail():
    # With MIN_UNIQUENESS_RATIO=0.15, we need many runs of the same single
    # item to get below 15%. 1 unique / 10 total = 10% < 15%.
    items = ["mother"]
    runs = [
        _record(freelist=_freelist(items=items), run_index=i)
        for i in range(10)
    ]
    failure = check_2_freelist_uniqueness(runs[0], runs)
    assert failure is not None
    assert failure.check_num == 2


# ─── Check 3: Pile-sort binary ──────────────────────────────────────

def test_check3_skips_placeholder():
    record = _record()  # Default pilesort is placeholder
    assert check_3_pilesort_binary(record) is None


def test_check3_pass_binary():
    record = _record(
        pilesort=_pilesort(matrix=[[0, 1], [1, 0]], collected=True),
    )
    assert check_3_pilesort_binary(record) is None


def test_check3_fail_non_binary():
    # Pydantic enforces list[list[int]], so non-binary values like 2 or 3
    # are the realistic failure case (not floats).
    record = _record(
        pilesort=_pilesort(matrix=[[0, 2], [2, 0]], collected=True),
    )
    failure = check_3_pilesort_binary(record)
    assert failure is not None
    assert failure.check_num == 3


# ─── Check 4: Pile-sort symmetric ───────────────────────────────────

def test_check4_skips_placeholder():
    record = _record()
    assert check_4_pilesort_symmetric(record) is None


def test_check4_pass_symmetric():
    record = _record(
        pilesort=_pilesort(matrix=[[1, 0], [0, 1]], collected=True),
    )
    assert check_4_pilesort_symmetric(record) is None


# ─── Check 5: Latency ───────────────────────────────────────────────

def test_check5_pass():
    record = _record(freelist=_freelist(latency_ms=5000))
    assert check_5_latency(record) is None


def test_check5_fail_high_latency():
    record = _record(freelist=_freelist(latency_ms=31000))
    failure = check_5_latency(record)
    assert failure is not None
    assert failure.check_num == 5


def test_check5_skips_placeholder_steps():
    record = _record(freelist=_freelist(latency_ms=100))
    # Pile sort and interview are placeholders (not_collected, 0ms)
    assert check_5_latency(record) is None


# ─── Check 6: Token consistency ──────────────────────────────────────

def test_check6_skips_placeholder():
    record = _record()
    assert check_6_token_consistency(record) is None


# ─── Check 7: Provider request ID ───────────────────────────────────

def test_check7_pass():
    record = _record(provider_request_id="msg_abc123")
    assert check_7_provider_request_id(record) is None


def test_check7_fail_empty():
    record = _record(provider_request_id="")
    failure = check_7_provider_request_id(record)
    assert failure is not None
    assert failure.check_num == 7


# ─── Integration: run_qa_checks ─────────────────────────────────────

def test_passing_record_no_failures():
    record = _record()
    failures = run_qa_checks(record)
    assert failures == []


def test_failing_record_has_failures():
    record = _record(
        freelist=_freelist(items=["a", "b"]),  # Only 2 items
        provider_request_id="",  # Empty
    )
    failures = run_qa_checks(record)
    assert len(failures) >= 2
    check_nums = {f.check_num for f in failures}
    assert 1 in check_nums
    assert 7 in check_nums


# ─── Slack posting ───────────────────────────────────────────────────

def test_slack_not_called_without_url():
    record = _record()
    failures = [
        type("F", (), {
            "check_num": 1, "description": "test", "threshold": "10",
            "actual": "5", "__str__": lambda s: "Check 1: test",
        })(),
    ]
    with patch.dict("os.environ", {}, clear=True):
        # Should not crash when URL is missing
        post_to_slack(record, failures, webhook_url=None)


def test_slack_called_with_url():
    record = _record()
    failures = [
        type("F", (), {
            "check_num": 1, "description": "test", "threshold": "10",
            "actual": "5", "__str__": lambda s: "Check 1: test",
        })(),
    ]
    with patch("scripts.qa_check.requests.post") as mock_post:
        mock_post.return_value.raise_for_status = lambda: None
        post_to_slack(record, failures, webhook_url="https://hooks.test/abc")
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://hooks.test/abc"
