"""Tests for QA check script. See ARCHITECTURE.md §4.1.6."""

from __future__ import annotations

import os
import time
from datetime import date, datetime
from pathlib import Path
from unittest.mock import patch

import pytest
from cdb_core import FreelistRecord, InformantRecord, InterviewRecord, PileSortRecord

# Import the check functions directly
import scripts.qa_check as _qa_check_module
from scripts.qa_check import (
    DENSE_TOKENIZER_MODEL_IDS,
    MAX_BACKUP_AGE_HOURS,
    MAX_LATENCY_MS,
    MAX_LATENCY_MS_REASONING,
    check_1_freelist_count,
    check_2_freelist_uniqueness,
    check_3_pilesort_binary,
    check_4_pilesort_symmetric,
    check_5_latency,
    check_6_token_consistency,
    check_7_provider_request_id,
    check_9_backup_freshness,
    check_record,
    post_infrastructure_alert,
    post_to_slack,
    run_infrastructure_checks,
    run_qa_checks,
    run_record_checks,
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
    record = _record(freelist=_freelist(latency_ms=61000))
    failure = check_5_latency(record)
    assert failure is not None
    assert failure.check_num == 5


def test_check5_skips_placeholder_steps():
    record = _record(freelist=_freelist(latency_ms=100))
    # Pile sort and interview are placeholders (not_collected, 0ms)
    assert check_5_latency(record) is None


def test_check_5_passes_at_45s_latency():
    """45 000 ms is within the new 60 000 ms ceiling -- must pass.

    Added 2026-04-21: ceiling raised from 30s to 60s (F2-T08). Gemini and
    DeepSeek 200-item pile-sort prompts legitimately take 30-45 seconds under
    normal load; the old 30s ceiling produced spurious Check 5 failures.
    """
    record = _record(freelist=_freelist(latency_ms=45000))
    assert check_5_latency(record) is None


# T1: Class-conditioned reasoning ceiling (CDA SME 2026-07-10 N1).

def _reasoning_freelist(latency_ms: int, thoughts_token_count: int = 5000) -> FreelistRecord:
    """FreelistRecord with thoughts_token_count > 0 (reasoning class)."""
    items = [f"item{i}" for i in range(15)]
    response_text = "1. " + "\n2. ".join(items)
    # visible_tokens = output_tokens - thoughts_token_count; keep visible near expected
    output_tokens = thoughts_token_count + max(1, round(len(response_text) / 4))
    return FreelistRecord(
        prompt_verbatim="test prompt",
        prompt_version="v1",
        response_verbatim=response_text,
        response_object_json={},
        input_tokens=50,
        output_tokens=output_tokens,
        thoughts_token_count=thoughts_token_count,
        latency_ms=latency_ms,
        stop_reason="end_turn",
        parsed_items=items,
        parsed_raw_order=items,
    )


def test_check5_non_reasoning_fails_at_base_ceiling_plus_one():
    """Non-reasoning step at MAX_LATENCY_MS + 1 ms fails (base ceiling unchanged)."""
    record = _record(freelist=_freelist(latency_ms=MAX_LATENCY_MS + 1))
    failure = check_5_latency(record)
    assert failure is not None
    assert failure.check_num == 5
    assert str(MAX_LATENCY_MS) in failure.threshold


def test_check5_reasoning_passes_at_300k():
    """Reasoning step at 300 000 ms passes under the reasoning ceiling (600 000 ms)."""
    record = _record(freelist=_reasoning_freelist(latency_ms=300_000))
    assert check_5_latency(record) is None


def test_check5_reasoning_fails_at_700k():
    """Reasoning step at 700 000 ms fails (above the reasoning ceiling of 600 000 ms)."""
    record = _record(freelist=_reasoning_freelist(latency_ms=700_000))
    failure = check_5_latency(record)
    assert failure is not None
    assert failure.check_num == 5
    assert str(MAX_LATENCY_MS_REASONING) in failure.threshold


def test_check5_per_step_ceiling_branches():
    """Each step branches independently: non-reasoning step with high latency fails
    even when the freelist step is a reasoning step that passes."""
    from cdb_core import InterviewRecord
    # freelist: reasoning, 200k ms -> PASS
    fl = _reasoning_freelist(latency_ms=200_000)
    # interview: non-reasoning, 61k ms -> FAIL (> MAX_LATENCY_MS)
    iv = InterviewRecord(
        prompt_verbatim="test",
        prompt_version="v1",
        response_verbatim="label",
        response_object_json={},
        input_tokens=10,
        output_tokens=1,
        thoughts_token_count=0,
        latency_ms=MAX_LATENCY_MS + 1000,
        stop_reason="end_turn",
        parsed_pile_labels=["label"],
    )
    record = _record(freelist=fl)
    # Swap interview into the record by rebuilding it
    record = record.model_copy(update={"interview": iv})
    failure = check_5_latency(record)
    assert failure is not None
    assert failure.check_num == 5
    assert "interview" in failure.description


# ─── Check 6: Token consistency ──────────────────────────────────────

def test_check6_skips_placeholder():
    record = _record()
    assert check_6_token_consistency(record) is None


# T2: Reasoning-aware Check 6 arithmetic (CDA SME 2026-07-10 N2).

def test_check6_non_reasoning_behavior_unchanged():
    """Non-reasoning step with output_tokens far from expected still fails."""
    items = [f"item{i}" for i in range(15)]
    response_text = "1. " + "\n2. ".join(items)
    # Deliberately set output_tokens 3x the expected value -> ratio > TOKEN_TOLERANCE
    expected = len(response_text) / 4
    fl = FreelistRecord(
        prompt_verbatim="test prompt",
        prompt_version="v1",
        response_verbatim=response_text,
        response_object_json={},
        input_tokens=50,
        output_tokens=int(expected * 4),  # 4x expected -> ratio=3 > 1.0
        thoughts_token_count=0,
        latency_ms=500,
        stop_reason="end_turn",
        parsed_items=items,
        parsed_raw_order=items,
    )
    record = _record(freelist=fl)
    failure = check_6_token_consistency(record)
    assert failure is not None
    assert failure.check_num == 6


def test_check6_reasoning_visible_tokens_match_expected():
    """Reasoning step with visible_tokens close to expected/4 passes Check 6.

    Batch-A fixture shape: thoughts=5000, output=5040, visible=40.
    response_verbatim ~160 chars -> expected~40 -> ratio=0 -> PASS.
    """
    response_text = (
        "1. mother\n2. father\n3. sister\n4. brother\n5. aunt\n"
        "6. uncle\n7. grandmother\n8. grandfather\n9. cousin\n10. niece\n"
        "11. nephew\n12. son\n13. daughter\n14. wife\n15. husband"
    )
    assert len(response_text) == 160  # expected=40.0 tokens
    fl = FreelistRecord(
        prompt_verbatim="test prompt",
        prompt_version="v1",
        response_verbatim=response_text,
        response_object_json={},
        input_tokens=50,
        output_tokens=5040,   # thoughts=5000, visible=40 -> matches expected
        thoughts_token_count=5000,
        latency_ms=500,
        stop_reason="end_turn",
        parsed_items=response_text.splitlines(),
        parsed_raw_order=response_text.splitlines(),
    )
    record = _record(freelist=fl)
    assert check_6_token_consistency(record) is None


def test_check6_reasoning_visible_tokens_skipped_when_zero():
    """When output_tokens == thoughts_token_count, visible_tokens=0 -> skip (not fail)."""
    fl = FreelistRecord(
        prompt_verbatim="test prompt",
        prompt_version="v1",
        response_verbatim="some visible content here",
        response_object_json={},
        input_tokens=50,
        output_tokens=5000,
        thoughts_token_count=5000,  # visible = 0
        latency_ms=500,
        stop_reason="end_turn",
        parsed_items=[f"item{i}" for i in range(15)],
        parsed_raw_order=[f"item{i}" for i in range(15)],
    )
    record = _record(freelist=fl)
    assert check_6_token_consistency(record) is None


def test_check6_reasoning_large_output_mismatch_fails_on_visible():
    """Reasoning step where visible_tokens is far from expected/4 fails.

    This verifies the arithmetic uses visible_tokens, not output_tokens.
    """
    fl = FreelistRecord(
        prompt_verbatim="test prompt",
        prompt_version="v1",
        response_verbatim="short",  # expected = 5/4 = 1.25
        response_object_json={},
        input_tokens=50,
        output_tokens=5100,   # thoughts=5000, visible=100 -> expected=1.25 -> ratio=79 -> FAIL
        thoughts_token_count=5000,
        latency_ms=500,
        stop_reason="end_turn",
        parsed_items=[f"item{i}" for i in range(15)],
        parsed_raw_order=[f"item{i}" for i in range(15)],
    )
    record = _record(freelist=fl)
    failure = check_6_token_consistency(record)
    assert failure is not None
    assert failure.check_num == 6


# T8: Dense-tokenizer Check 6 branch (CDA SME 2026-07-10 addendum N8/N9).

def test_dense_tokenizer_model_ids_bare_strings():
    """DENSE_TOKENIZER_MODEL_IDS contains bare model_ids (no provider prefix).

    Verified against wave-3 InformantRecord.model_id fields (addendum N8).
    """
    assert "claude-opus-4-8" in DENSE_TOKENIZER_MODEL_IDS
    assert "claude-sonnet-5" in DENSE_TOKENIZER_MODEL_IDS
    # No provider-prefixed form in the set.
    assert "anthropic/claude-opus-4-8" not in DENSE_TOKENIZER_MODEL_IDS
    assert "anthropic/claude-sonnet-5" not in DENSE_TOKENIZER_MODEL_IDS


def _dense_freelist(output_tokens: int, thoughts: int = 0, latency_ms: int = 500) -> FreelistRecord:
    """FreelistRecord with a 160-char response for dense-tokenizer arithmetic tests."""
    rv = (
        "1. mother\n2. father\n3. sister\n4. brother\n5. aunt\n"
        "6. uncle\n7. grandmother\n8. grandfather\n9. cousin\n10. niece\n"
        "11. nephew\n12. son\n13. daughter\n14. wife\n15. husband"
    )
    assert len(rv) == 160  # expected_dense = 160/1.75 = 91.43
    items = [f"item{i}" for i in range(15)]
    return FreelistRecord(
        prompt_verbatim="test prompt",
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


def _dense_record(model_id: str, **fl_kwargs: object) -> object:
    """InformantRecord for a dense-tokenizer model."""
    fl = _dense_freelist(**fl_kwargs)  # type: ignore[arg-type]
    return _record(freelist=fl, model_id=model_id)


def test_check6_dense_pass_at_1_7_chars_per_token():
    """Dense-tokenizer model at ~1.7 chars/token passes Check 6 under the N9 branch.

    160-char response / 1.75 -> expected=91.43. output_tokens=91 -> ratio=0.005 -> PASS.
    Under the old chars/4 heuristic: expected=40, ratio=1.275 -> FAIL.
    """
    record = _dense_record("claude-sonnet-5", output_tokens=91)
    assert check_6_token_consistency(record) is None


def test_check6_dense_fails_without_branch():
    """The same record (output=91) would fail Check 6 on a non-dense model.

    This verifies the N9 branch is responsible for the PASS, not the tolerance band.
    """
    # Same freelist, non-dense model_id: expected=40, ratio=1.275 > 1.0 -> FAIL
    record = _dense_record("test/non-dense-model", output_tokens=91)
    failure = check_6_token_consistency(record)
    assert failure is not None
    assert failure.check_num == 6


def test_check6_dense_and_reasoning_compose():
    """Dense (N9) and reasoning (N2) branches compose for a record that is both.

    visible_tokens = 5091 - 5000 = 91; expected_dense = 160/1.75 = 91.43.
    ratio = |91 - 91.43| / 91.43 = 0.005 -> PASS.
    """
    record = _dense_record("claude-sonnet-5", output_tokens=5091, thoughts=5000, latency_ms=257_000)
    assert check_6_token_consistency(record) is None


def test_check6_dense_expected_shows_dense_divisor_in_failure():
    """When a dense record genuinely fails Check 6, the threshold uses the dense expected."""
    # 160 chars / 1.75 = 91.43 expected. output=300 -> ratio=|300-91.43|/91.43=2.28 -> FAIL
    record = _dense_record("claude-sonnet-5", output_tokens=300)
    failure = check_6_token_consistency(record)
    assert failure is not None
    assert failure.check_num == 6
    # The threshold references the dense expected (~91), not the standard (~40).
    assert "91" in failure.threshold


def test_check6_non_dense_unchanged():
    """Non-dense models still use the chars/4 heuristic; N9 does not affect them."""
    items = [f"item{i}" for i in range(15)]
    response_text = "1. " + "\n2. ".join(items)
    expected = len(response_text) / 4
    output_tokens = int(expected)  # Exactly at expected -> ratio=0 -> PASS
    fl = FreelistRecord(
        prompt_verbatim="test prompt",
        prompt_version="v1",
        response_verbatim=response_text,
        response_object_json={},
        input_tokens=50,
        output_tokens=output_tokens,
        thoughts_token_count=0,
        latency_ms=500,
        stop_reason="end_turn",
        parsed_items=items,
        parsed_raw_order=items,
    )
    record = _record(freelist=fl)  # model_id="claude-opus-4-6" (non-dense)
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


# ─── Integration: run_record_checks ─────────────────────────────────

def test_passing_record_no_failures():
    record = _record()
    failures = run_record_checks(record)
    assert failures == []


def test_failing_record_has_failures():
    record = _record(
        freelist=_freelist(items=["a", "b"]),  # Only 2 items
        provider_request_id="",  # Empty
    )
    failures = run_record_checks(record)
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


# ─── Check 8: Salience agreement (aggregate, per (model, domain)) ───

def test_check8_stable_items_pass():
    """Identical free lists across runs → rho ≈ 1 → no failure.

    Uses 12 items (above the MIN_SALIENCE_AGREEMENT_SHARED_ITEMS floor
    of 10) so that the rho computation actually runs — if the floor
    short-circuits before rho is computed, the test is testing the
    bypass path rather than the happy path.
    """
    from scripts.qa_check import check_salience_agreement
    items = [
        "mother", "father", "sister", "brother", "uncle", "aunt",
        "grandmother", "grandfather", "cousin", "niece", "nephew", "stepmother",
    ]
    records = [_record(freelist=_freelist(items), run_index=i) for i in range(4)]
    rho, failure = check_salience_agreement(records, "claude-opus-4-6", "family")
    assert failure is None
    assert rho >= 0.85


def test_check8_too_few_items_bypasses():
    """Groups with fewer than MIN_SALIENCE_AGREEMENT_SHARED_ITEMS distinct
    items across the group's free lists return (1.0, None) — the check
    is skipped because Spearman ρ on a short ranking is too noisy to
    interpret. Per SME review of the Sutrop wiring PR (2026-04-20)."""
    from scripts.qa_check import check_salience_agreement
    items = ["a", "b", "c", "d", "e"]  # 5 items < 10
    records = [_record(freelist=_freelist(items), run_index=i) for i in range(4)]
    rho, failure = check_salience_agreement(records, "claude-opus-4-6", "family")
    assert failure is None
    assert rho == 1.0


def test_check8_single_record_returns_na():
    """Fewer than 2 records → rho is not meaningful; no failure posted."""
    from scripts.qa_check import check_salience_agreement
    records = [_record()]
    rho, failure = check_salience_agreement(records, "claude-opus-4-6", "family")
    assert failure is None
    assert rho == 1.0


def test_check8_failure_shape_when_rho_below_threshold():
    """When compute_salience_agreement returns ρ < 0.85, the QAFailure
    object carries Check 8 metadata with the right description, threshold,
    and actual value. The rho computation is tested elsewhere (in
    test_sme_measures.py); this test pins only the qa_check failure
    shape deterministically by mocking the agreement computation —
    per SME review of the Sutrop wiring PR (2026-04-20).
    """
    from scripts.qa_check import check_salience_agreement
    items = [f"i{i}" for i in range(12)]
    records = [_record(freelist=_freelist(items), run_index=i) for i in range(4)]
    with patch(
        "cdb_analyze.salience.compute_salience_agreement",
        return_value=0.70,
    ):
        rho, failure = check_salience_agreement(
            records, "claude-opus-4-6", "family",
        )
    assert rho == 0.70
    assert failure is not None
    assert failure.check_num == 8
    assert "Smith" in failure.description
    assert "Sutrop" in failure.description
    assert failure.threshold == ">= 0.85"
    assert failure.actual == "0.700"


def test_check8_aggregate_runs_group_by_model_domain():
    """run_aggregate_checks groups records by (model_id, domain_slug)
    and runs Check 8 on each group. No Slack URL → stderr fallback.

    Uses 12 items per group (above MIN_SALIENCE_AGREEMENT_SHARED_ITEMS)
    so each group actually computes ρ rather than short-circuiting on
    the item-count floor.
    """
    from scripts.qa_check import run_aggregate_checks
    items = [f"item_{i}" for i in range(12)]
    records = [
        _record(freelist=_freelist(items), model_id="m1", run_index=i)
        for i in range(3)
    ] + [
        _record(freelist=_freelist(items), model_id="m2", run_index=i)
        for i in range(3)
    ]
    # No webhook URL → falls through to stderr; should not raise
    n_failed = run_aggregate_checks(records)
    # Stable items across runs → ρ ≈ 1 → zero failures expected
    assert n_failed == 0


def test_aggregate_alert_posts_expected_fields():
    from scripts.qa_check import QAFailure, post_aggregate_alert
    failure = QAFailure(
        8,
        "Smith's S / Sutrop CSI rank orders diverge significantly",
        ">= 0.85",
        "0.712",
    )
    with patch("scripts.qa_check.requests.post") as mock_post:
        mock_post.return_value.raise_for_status = lambda: None
        post_aggregate_alert(
            "claude-opus-4-6",
            "family",
            failure,
            rho=0.712,
            webhook_url="https://hooks.test/abc",
        )
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://hooks.test/abc"
        payload_text = call_args[1]["json"]["text"]
        assert "claude-opus-4-6" in payload_text
        assert "family" in payload_text
        assert "0.712" in payload_text
        assert "0.85" in payload_text


# ─── Check 9: Backup freshness ───────────────────────────────────────

def test_check9_log_missing_returns_failure(tmp_path: Path) -> None:
    """No backup log → QAFailure with check_num 9 and 'missing' in actual."""
    nonexistent = tmp_path / "backup.log"
    failure = check_9_backup_freshness(log_path=nonexistent)
    assert failure is not None
    assert failure.check_num == 9
    assert "missing" in failure.actual.lower()


def test_check9_log_49h_old_returns_failure(tmp_path: Path) -> None:
    """Log with mtime 49h ago → QAFailure; actual message includes '49.0'."""
    log_file = tmp_path / "backup.log"
    log_file.write_text("backup ok\n", encoding="utf-8")

    # Set mtime to 49 hours ago
    age_seconds = 49 * 3600
    past_time = time.time() - age_seconds
    os.utime(log_file, (past_time, past_time))

    failure = check_9_backup_freshness(log_path=log_file)
    assert failure is not None
    assert failure.check_num == 9
    assert "49.0" in failure.actual


def test_check9_log_1h_old_passes(tmp_path: Path) -> None:
    """Log with mtime 1h ago → PASS (None)."""
    log_file = tmp_path / "backup.log"
    log_file.write_text("backup ok\n", encoding="utf-8")

    age_seconds = 1 * 3600
    past_time = time.time() - age_seconds
    os.utime(log_file, (past_time, past_time))

    assert check_9_backup_freshness(log_path=log_file) is None


def test_check9_log_exactly_48h_returns_failure(tmp_path: Path) -> None:
    """Log mtime exactly at MAX_BACKUP_AGE_HOURS → QAFailure (boundary is >=)."""
    log_file = tmp_path / "backup.log"
    log_file.write_text("backup ok\n", encoding="utf-8")

    age_seconds = MAX_BACKUP_AGE_HOURS * 3600
    past_time = time.time() - age_seconds
    os.utime(log_file, (past_time, past_time))

    failure = check_9_backup_freshness(log_path=log_file)
    assert failure is not None
    assert failure.check_num == 9


# ─── New split tests (task #F2-T11) ─────────────────────────────────

def test_infrastructure_check_returns_check_9_when_log_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """run_infrastructure_checks returns exactly one QAFailure with check_num==9
    when _BACKUP_LOG_PATH points to a nonexistent file."""
    nonexistent = tmp_path / "backup.log"
    monkeypatch.setattr(_qa_check_module, "_BACKUP_LOG_PATH", nonexistent)
    failures = run_infrastructure_checks()
    assert len(failures) == 1
    assert failures[0].check_num == 9


def test_run_record_checks_does_not_invoke_check_9(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """run_record_checks never produces a QAFailure with check_num==9, even when
    _BACKUP_LOG_PATH points to a nonexistent file."""
    nonexistent = tmp_path / "backup.log"
    monkeypatch.setattr(_qa_check_module, "_BACKUP_LOG_PATH", nonexistent)
    record = _record()
    failures = run_record_checks(record)
    check_nines = [f for f in failures if f.check_num == 9]
    assert check_nines == [], (
        f"run_record_checks must not invoke check 9; got: {check_nines}"
    )


def test_post_infrastructure_alert_posts_expected_fields() -> None:
    """post_infrastructure_alert posts to #lsb-alerts with the 'QA Infrastructure
    Failure' header and includes check name, threshold, and actual value."""
    from scripts.qa_check import QAFailure
    failure = QAFailure(
        9,
        "Backup log missing",
        f"< {MAX_BACKUP_AGE_HOURS}h since last backup",
        "backup log missing: /opt/lsb-agent/logs/backup.log",
    )
    with patch("scripts.qa_check.requests.post") as mock_post:
        mock_post.return_value.raise_for_status = lambda: None
        post_infrastructure_alert(failure, webhook_url="https://hooks.test/infra")
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://hooks.test/infra"
        payload_text = call_args[1]["json"]["text"]
        assert "QA Infrastructure Failure" in payload_text
        assert "Backup log missing" in payload_text
        assert str(MAX_BACKUP_AGE_HOURS) in payload_text
        assert "backup log missing" in payload_text


# ─── Follow-up coverage tests (task #F2-T11 tester audit) ────────────

def test_run_qa_checks_shim_concatenates_check_9_failures(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """run_qa_checks (the deprecated compat shim) must concatenate check 9 results
    with checks 1–8. When _BACKUP_LOG_PATH is missing, the shim must include a
    QAFailure with check_num==9 in its output — proving both batteries are called.

    Regression guard: if the shim's concatenation is broken (e.g., only calls
    run_record_checks), this test will catch it immediately.
    """
    nonexistent = tmp_path / "backup.log"
    monkeypatch.setattr(_qa_check_module, "_BACKUP_LOG_PATH", nonexistent)
    record = _record()
    failures = run_qa_checks(record)
    check_nines = [f for f in failures if f.check_num == 9]
    assert len(check_nines) == 1, (
        "run_qa_checks shim must include check 9 failures; "
        f"got check_nums: {[f.check_num for f in failures]}"
    )


def test_check_record_does_not_route_check_9_through_post_to_slack(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """check_record (the per-record CLI helper at qa_check.py line 456) must call
    only run_record_checks (checks 1–8). When backup.log is absent, check_record
    must return True (no failures) and must NOT invoke post_to_slack.

    This verifies that infrastructure failures are not routed through the
    per-record alert path — the distinction mandated by the SME mandatory note 2
    and the architecture of post_infrastructure_alert vs post_to_slack.
    """
    nonexistent = tmp_path / "backup.log"
    monkeypatch.setattr(_qa_check_module, "_BACKUP_LOG_PATH", nonexistent)
    record = _record()
    with patch("scripts.qa_check.requests.post") as mock_post:
        result = check_record(record, all_records=None)
    assert result is True, (
        "check_record must return True for a structurally valid record "
        "even when backup.log is absent"
    )
    mock_post.assert_not_called(), (
        "check_record must not call post_to_slack (requests.post) "
        "for a check-9 infrastructure condition"
    )


# ─── Gap coverage: dense+reasoning branch composition ────────────────────────
# N9 (addendum) states that the two class-conditioning branches in Check 6
# compose additively and orthogonally: N2 subtracts reasoning tokens first,
# then N9 applies the denser expected chars-per-token. Check 5 is unaffected
# by the dense class; only thoughts_token_count > 0 controls the ceiling.
# The tests below exercise claude-opus-4-8 (the second dense-roster model)
# with thoughts_token_count > 0 to verify no accidental cross-branch
# interference between the dense and reasoning paths.

def _dense_reasoning_freelist(
    *,
    output_tokens: int,
    thoughts: int,
    latency_ms: int,
) -> FreelistRecord:
    """FreelistRecord with a 160-char response, dense+reasoning token shape."""
    rv = (
        "1. mother\n2. father\n3. sister\n4. brother\n5. aunt\n"
        "6. uncle\n7. grandmother\n8. grandfather\n9. cousin\n10. niece\n"
        "11. nephew\n12. son\n13. daughter\n14. wife\n15. husband"
    )
    assert len(rv) == 160
    return FreelistRecord(
        prompt_verbatim="test prompt",
        prompt_version="v1",
        response_verbatim=rv,
        response_object_json={},
        input_tokens=50,
        output_tokens=output_tokens,
        thoughts_token_count=thoughts,
        latency_ms=latency_ms,
        stop_reason="end_turn",
        parsed_items=[f"item{i}" for i in range(15)],
        parsed_raw_order=[f"item{i}" for i in range(15)],
    )


def test_check5_dense_class_reasoning_uses_reasoning_ceiling():
    """Check 5 uses MAX_LATENCY_MS_REASONING for claude-opus-4-8 with thoughts > 0.

    The dense class has no special handling in Check 5; the reasoning ceiling
    applies solely because thoughts_token_count > 0 (N1). A latency between the
    base ceiling (60_000 ms) and the reasoning ceiling (600_000 ms) must PASS.

    Without the reasoning branch: 300_000 > MAX_LATENCY_MS=60_000 -> FAIL.
    With the reasoning branch: 300_000 < MAX_LATENCY_MS_REASONING=600_000 -> PASS.
    Verifies dense-class routing does not interfere with the Check 5 ceiling.
    """
    fl = _dense_reasoning_freelist(output_tokens=5091, thoughts=5000, latency_ms=300_000)
    record = _record(freelist=fl, model_id="claude-opus-4-8")
    assert check_5_latency(record) is None


def test_check6_claude_opus_48_dense_and_reasoning_compose():
    """N2 and N9 compose correctly for claude-opus-4-8 (dense + reasoning).

    N2: visible_tokens = 5091 - 5000 = 91.
    N9: expected_dense = 160 / 1.75 = 91.43.
    ratio = |91 - 91.43| / 91.43 = 0.005 -> within TOKEN_TOLERANCE=1.0 -> PASS.

    Without N2: actual=5091, expected_dense=91.43 -> ratio=54.7 -> FAIL.
    Without N9: visible=91, expected_std=160/4=40 -> ratio=1.275 -> FAIL.
    Only the composition of both branches produces PASS.
    """
    fl = _dense_reasoning_freelist(output_tokens=5091, thoughts=5000, latency_ms=257_000)
    record = _record(freelist=fl, model_id="claude-opus-4-8")
    assert check_6_token_consistency(record) is None


def test_check6_claude_opus_48_dense_reasoning_genuine_fail_still_fails():
    """A claude-opus-4-8 record whose visible tokens deviate beyond tolerance fails.

    visible_tokens = 5300 - 5000 = 300; expected_dense = 160/1.75 = 91.43.
    ratio = |300 - 91.43| / 91.43 = 2.28 -> exceeds TOKEN_TOLERANCE=1.0 -> FAIL.
    Confirms the composed branches still catch genuine data-quality failures.
    """
    fl = _dense_reasoning_freelist(output_tokens=5300, thoughts=5000, latency_ms=257_000)
    record = _record(freelist=fl, model_id="claude-opus-4-8")
    failure = check_6_token_consistency(record)
    assert failure is not None
    assert failure.check_num == 6
