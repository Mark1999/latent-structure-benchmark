"""Tests for QA check script. See ARCHITECTURE.md §4.1.6."""

from __future__ import annotations

import os
import time
from datetime import date, datetime
from pathlib import Path
from unittest.mock import patch

from cdb_core import FreelistRecord, InformantRecord, InterviewRecord, PileSortRecord

# Import the check functions directly
from scripts.qa_check import (
    MAX_BACKUP_AGE_HOURS,
    check_1_freelist_count,
    check_2_freelist_uniqueness,
    check_3_pilesort_binary,
    check_4_pilesort_symmetric,
    check_5_latency,
    check_6_token_consistency,
    check_7_provider_request_id,
    check_9_backup_freshness,
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
    record = _record(freelist=_freelist(latency_ms=61000))
    failure = check_5_latency(record)
    assert failure is not None
    assert failure.check_num == 5


def test_check5_skips_placeholder_steps():
    record = _record(freelist=_freelist(latency_ms=100))
    # Pile sort and interview are placeholders (not_collected, 0ms)
    assert check_5_latency(record) is None


def test_check_5_passes_at_45s_latency():
    """45 000 ms is within the new 60 000 ms ceiling — must pass.

    Added 2026-04-21: ceiling raised from 30s to 60s (F2-T08). Gemini and
    DeepSeek 200-item pile-sort prompts legitimately take 30-45 seconds under
    normal load; the old 30s ceiling produced spurious Check 5 failures.
    """
    record = _record(freelist=_freelist(latency_ms=45000))
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
