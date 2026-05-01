"""Tests for the collection runner. Uses mock adapter — no real API calls."""

import asyncio
import hashlib
import json
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from cdb_collect.adapters.base import AdapterResult
from cdb_collect.runner import run_baseline_sort, run_informant, run_two_pass
from cdb_core import Domain, InformantRecord, ModelRef

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


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
        truncation_k=5,  # Small for test manageability
    )


def _free_list_result() -> AdapterResult:
    # 10 items so check_1 (MIN_FREELIST_ITEMS=10) passes in the assembled record.
    text = (
        "1. Mother\n2. Father\n3. Sister\n4. Brother\n5. Aunt\n"
        "6. Uncle\n7. Grandmother\n8. Grandfather\n9. Cousin\n10. Niece"
    )
    return AdapterResult(
        text=text,
        raw_response={"id": "msg_free", "content": [{"text": text}]},
        latency_ms=350,
        cost_usd=0.01,
        input_tokens=87,
        output_tokens=30,
        provider_request_id="msg_free_123",
        model_version_returned="claude-opus-4-6-20260401",
        stop_reason="end_turn",
    )


def _pile_sort_result() -> AdapterResult:
    # Matches the 10-item free list so the pile sort parser validates all items.
    piles_json = json.dumps({
        "piles": [
            ["mother", "father"],
            ["sister", "brother"],
            ["aunt", "uncle"],
            ["grandmother", "grandfather", "cousin", "niece"],
        ],
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
    # 4 labels matching 4 piles from _pile_sort_result.
    text = "1. Parents\n2. Siblings\n3. Aunts and Uncles\n4. Extended family"
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


def _mock_adapter() -> MagicMock:
    """Mock adapter dispatches responses based on call order."""
    adapter = MagicMock()
    adapter.model = _model_ref()

    call_count = 0

    async def mock_complete(prompt, *, json_schema=None, temperature=0.7):
        nonlocal call_count
        call_count += 1
        lower = prompt.lower()
        # Interview prompt asks for "label" / "organizing principle"
        if "label" in lower or "organizing principle" in lower:
            return _interview_result()
        # Pile sort prompt asks to "sort" items
        elif "sort" in lower:
            return _pile_sort_result()
        # Free list prompt asks to "list"
        else:
            return _free_list_result()

    adapter.complete = mock_complete
    return adapter


# ─── Single-pass tests ──────────────────────────────────────────────


def test_run_informant_full_protocol():
    record = asyncio.run(run_informant(_mock_adapter(), _domain(), 0))

    assert record.collection_mode == "single_pass"
    assert record.domain_slug == "family"
    assert len(record.freelist.parsed_items) == 10
    assert record.pile_sort.stop_reason == "end_turn"
    assert len(record.pile_sort.parsed_piles) == 4
    assert record.interview.stop_reason == "end_turn"
    assert len(record.interview.parsed_pile_labels) == 4
    assert record.pile_sort.item_source == "own_freelist"


def test_run_informant_default_temperature_and_empty_qa_notes():
    """Without overrides, temperature=0.7 (dominant step) and qa_notes is empty."""
    record = asyncio.run(run_informant(_mock_adapter(), _domain(), 0))
    assert record.temperature == 0.7
    assert record.qa_notes == ""


def test_run_informant_temperature_override_recorded():
    """--temperature 0.0 → record.temperature = 0.0."""
    record = asyncio.run(
        run_informant(_mock_adapter(), _domain(), 0, temperature=0.0),
    )
    assert record.temperature == 0.0


def test_run_informant_temperature_override_propagates_to_adapter():
    """Override temperature reaches adapter.complete on all three steps."""
    adapter = _mock_adapter()
    seen_temperatures = []

    async def capture_complete(prompt, *, json_schema=None, temperature=0.7):
        seen_temperatures.append(temperature)
        lower = prompt.lower()
        if "label" in lower or "organizing principle" in lower:
            return _interview_result()
        if "sort" in lower:
            return _pile_sort_result()
        return _free_list_result()

    adapter.complete = capture_complete

    asyncio.run(run_informant(adapter, _domain(), 0, temperature=0.0))

    assert len(seen_temperatures) == 3  # one per CDA step
    assert all(t == 0.0 for t in seen_temperatures), (
        f"Expected all three steps at temperature=0.0, got {seen_temperatures}"
    )


def test_run_informant_campaign_id_written_to_qa_notes():
    """--campaign-id shakedown-20260420 → qa_notes='campaign_id=shakedown-20260420'."""
    record = asyncio.run(
        run_informant(
            _mock_adapter(), _domain(), 0,
            campaign_id="shakedown-20260420",
        ),
    )
    assert record.qa_notes == "campaign_id=shakedown-20260420"


def test_run_informant_temperature_and_campaign_id_together():
    """Both overrides compose (the actual shakedown determinism-cell invocation)."""
    record = asyncio.run(
        run_informant(
            _mock_adapter(), _domain(), 0,
            temperature=0.0,
            campaign_id="shakedown-20260420",
        ),
    )
    assert record.temperature == 0.0
    assert record.qa_notes == "campaign_id=shakedown-20260420"


def test_run_informant_manifest_no_empty_hashes():
    record = asyncio.run(run_informant(_mock_adapter(), _domain(), 0))
    empty_hash = hashlib.sha256(b"").hexdigest()
    for key, value in record.sha256_manifest.items():
        assert value != empty_hash, f"Manifest key {key!r} has empty-string hash"


def test_run_informant_round_trip():
    record = asyncio.run(run_informant(_mock_adapter(), _domain(), 0))
    json_str = record.model_dump_json()
    restored = InformantRecord.model_validate_json(json_str)
    assert restored.informant_id == record.informant_id
    assert restored.collection_mode == "single_pass"


# ─── Two-pass tests ─────────────────────────────────────────────────


def test_two_pass_returns_all_records():
    records = asyncio.run(
        run_two_pass(_mock_adapter(), _domain(), n_free_lists=2, n_pile_sorts=2)
    )
    assert len(records) == 4  # 2 free-list + 2 pile-sort
    for r in records:
        assert r.collection_mode == "two_pass"


def test_two_pass_free_list_records_have_placeholders():
    records = asyncio.run(
        run_two_pass(_mock_adapter(), _domain(), n_free_lists=2, n_pile_sorts=1)
    )
    # First 2 are free-list-only
    for r in records[:2]:
        assert r.pile_sort.stop_reason == "not_collected"
        assert r.freelist.stop_reason == "end_turn"


def test_two_pass_pile_sort_records_use_consensus():
    records = asyncio.run(
        run_two_pass(_mock_adapter(), _domain(), n_free_lists=2, n_pile_sorts=2)
    )
    # Last 2 are pile-sort records
    for r in records[2:]:
        assert r.pile_sort.stop_reason == "end_turn"
        assert r.pile_sort.item_source == "consensus:claude-opus-4-6"
        assert r.interview.stop_reason == "end_turn"


# ─── Baseline sort tests ────────────────────────────────────────────


def test_baseline_sort_returns_records():
    items = ["mother", "father", "sister", "brother", "aunt"]
    records = asyncio.run(
        run_baseline_sort(
            _mock_adapter(), _domain(),
            items=items, baseline_id="romney_1996", n_sorts=2,
        )
    )
    assert len(records) == 2
    for r in records:
        assert r.collection_mode == "baseline_items"
        assert r.pile_sort.item_source == "baseline:romney_1996"
        assert r.pile_sort.stop_reason == "end_turn"
        assert r.freelist.stop_reason == "not_collected"


# ─── Regression: check 9 must not affect runner qa_passed (task #F2-T11) ───


def test_run_informant_no_backup_log_does_not_fail_qa(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Even when logs/backup.log is absent, run_informant produces a record with
    qa_passed=True (and empty qa_notes, or only the campaign_id tag if supplied).

    Regression test for the infrastructure-split: the runner calls only
    run_record_checks (checks 1–8), never run_infrastructure_checks (check 9).
    A missing backup log is an operator-environment condition; it must not
    corrupt the per-record qa_passed verdict.
    """
    import scripts.qa_check as _qa_check_module  # noqa: PLC0415
    nonexistent_log = tmp_path / "backup.log"
    monkeypatch.setattr(_qa_check_module, "_BACKUP_LOG_PATH", nonexistent_log)

    record = asyncio.run(run_informant(_mock_adapter(), _domain(), 0))
    assert record.qa_passed is True
    assert record.qa_notes == ""
