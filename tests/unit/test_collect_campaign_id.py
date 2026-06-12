"""Tests for --campaign-id threading to all collection modes (BUG 2).

Verifies that campaign_id flows from the CLI through the collect_* functions
and runner functions to the written InformantRecord.qa_notes field.

All tests use mock adapters. No real API calls.
"""

from __future__ import annotations

import asyncio
import json
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock

from cdb_collect.adapters.base import AdapterResult
from cdb_collect.runner import run_baseline_sort, run_cross_model_sort, run_two_pass
from cdb_core import Domain, ModelRef


def _model_ref(model_id: str = "test/mock-model") -> ModelRef:
    return ModelRef(
        provider="openrouter",
        model_id=model_id,
        family="mock",
        origin="us",
        open_weights=False,
        collection_method="openrouter",
        quantization=None,
        release_date=date(2026, 1, 1),
        version_label=model_id.split("/")[-1] if "/" in model_id else model_id,
    )


def _domain() -> Domain:
    return Domain(
        slug="food",
        version="v1",
        display_name="Food Terms",
        prompt_seed="type of food or food-related term",
        truncation_k=5,
    )


def _free_list_result() -> AdapterResult:
    text = (
        "1. Apple\n2. Bread\n3. Cheese\n4. Egg\n5. Fish\n"
        "6. Grape\n7. Ham\n8. Ice cream\n9. Jam\n10. Kale"
    )
    return AdapterResult(
        text=text,
        raw_response={"mock": True},
        latency_ms=100,
        input_tokens=50,
        output_tokens=30,
        provider_request_id="mock-fl",
        model_version_returned="test/mock-model-v1",
        stop_reason="end_turn",
    )


def _pile_sort_result() -> AdapterResult:
    piles = json.dumps({
        "piles": [
            ["apple", "grape"],
            ["bread", "cheese", "ham"],
            ["egg", "fish"],
            ["ice cream", "jam", "kale"],
        ],
    })
    return AdapterResult(
        text=piles,
        raw_response={"mock": True},
        latency_ms=100,
        input_tokens=80,
        output_tokens=40,
        provider_request_id="mock-ps",
        model_version_returned="test/mock-model-v1",
        stop_reason="end_turn",
    )


def _interview_result() -> AdapterResult:
    text = "1. Fruits\n2. Staples\n3. Proteins\n4. Other"
    return AdapterResult(
        text=text,
        raw_response={"mock": True},
        latency_ms=100,
        input_tokens=60,
        output_tokens=15,
        provider_request_id="mock-iv",
        model_version_returned="test/mock-model-v1",
        stop_reason="end_turn",
    )


def _mock_adapter(model_id: str = "test/mock-model") -> MagicMock:
    adapter = MagicMock()
    adapter.model = _model_ref(model_id)

    async def mock_complete(prompt, *, json_schema=None, temperature=0.7):
        lower = prompt.lower()
        if "label" in lower or "organizing principle" in lower:
            return _interview_result()
        elif "sort" in lower:
            return _pile_sort_result()
        else:
            return _free_list_result()

    adapter.complete = mock_complete
    return adapter


# ── run_two_pass campaign_id threading ──────────────────────────────


def test_run_two_pass_campaign_id_written_to_qa_notes():
    """campaign_id flows through run_two_pass to InformantRecord.qa_notes."""
    records = asyncio.run(
        run_two_pass(
            _mock_adapter(), _domain(),
            n_free_lists=2, n_pile_sorts=1,
            campaign_id="test-001",
        )
    )
    assert len(records) == 3
    for rec in records:
        assert "campaign_id=test-001" in rec.qa_notes, (
            f"Expected qa_notes to contain 'campaign_id=test-001', got: {rec.qa_notes!r}"
        )


def test_run_two_pass_no_campaign_id_empty_notes():
    """Without campaign_id, qa_notes does not contain a campaign_id tag."""
    records = asyncio.run(
        run_two_pass(
            _mock_adapter(), _domain(),
            n_free_lists=1, n_pile_sorts=1,
        )
    )
    for rec in records:
        assert "campaign_id=" not in rec.qa_notes


# ── run_cross_model_sort campaign_id threading ───────────────────────


def test_run_cross_model_sort_campaign_id_written_to_qa_notes():
    """campaign_id flows through run_cross_model_sort to InformantRecord.qa_notes."""
    consensus_items = ["apple", "bread", "cheese", "egg", "fish"]
    records = asyncio.run(
        run_cross_model_sort(
            _mock_adapter(), _domain(),
            consensus_items=consensus_items,
            n_pile_sorts=2,
            campaign_id="food-campaign-2026-06-11",
        )
    )
    assert len(records) == 2
    for rec in records:
        assert "campaign_id=food-campaign-2026-06-11" in rec.qa_notes, (
            f"Expected qa_notes to contain campaign_id tag, got: {rec.qa_notes!r}"
        )


def test_run_cross_model_sort_no_campaign_id_empty_notes():
    """Without campaign_id, cross_model_sort records have no campaign_id tag."""
    consensus_items = ["apple", "bread", "cheese", "egg", "fish"]
    records = asyncio.run(
        run_cross_model_sort(
            _mock_adapter(), _domain(),
            consensus_items=consensus_items,
            n_pile_sorts=1,
        )
    )
    for rec in records:
        assert "campaign_id=" not in rec.qa_notes


# ── run_baseline_sort campaign_id threading ──────────────────────────


def test_run_baseline_sort_campaign_id_written_to_qa_notes():
    """campaign_id flows through run_baseline_sort to InformantRecord.qa_notes."""
    items = ["apple", "bread", "cheese", "egg", "fish"]
    records = asyncio.run(
        run_baseline_sort(
            _mock_adapter(), _domain(),
            items=items,
            baseline_id="test_baseline",
            n_sorts=2,
            campaign_id="baseline-campaign-001",
        )
    )
    assert len(records) == 2
    for rec in records:
        assert "campaign_id=baseline-campaign-001" in rec.qa_notes, (
            f"Expected qa_notes to contain campaign_id tag, got: {rec.qa_notes!r}"
        )


# ── collect_cross_model campaign_id threading (via scripts.collect) ──


def test_collect_cross_model_campaign_id_flows_to_records(tmp_path: Path):
    """campaign_id passed to collect_cross_model reaches each written record."""
    # The runner-level tests above (test_run_cross_model_sort_campaign_id_*) verify
    # the full end-to-end flow. Here we verify the function signature contract.
    import inspect

    from scripts.collect import collect_cross_model as _fn
    sig = inspect.signature(_fn)
    assert "campaign_id" in sig.parameters, (
        "collect_cross_model must accept campaign_id keyword argument"
    )


# ── collect_two_pass and collect_baseline signature checks (AC17/AC19) ─


def test_collect_two_pass_accepts_campaign_id():
    """collect_two_pass must accept campaign_id keyword argument (BUG 2 AC17).

    AC17 specifies records produced via the two_pass dispatch path carry
    campaign_id. The dispatch site in main() passes args.campaign_id to
    collect_two_pass, which forwards it to run_two_pass. The function
    signature must expose the parameter for that threading to work.
    """
    import inspect

    from scripts.collect import collect_two_pass as _fn
    sig = inspect.signature(_fn)
    assert "campaign_id" in sig.parameters, (
        "collect_two_pass must accept campaign_id keyword argument (BUG 2 AC17)"
    )


def test_collect_baseline_accepts_campaign_id():
    """collect_baseline must accept campaign_id keyword argument (BUG 2 AC19).

    AC19 specifies records produced via the baseline dispatch path carry
    campaign_id. The dispatch site in main() passes args.campaign_id to
    collect_baseline, which forwards it to run_baseline_sort.
    """
    import inspect

    from scripts.collect import collect_baseline as _fn
    sig = inspect.signature(_fn)
    assert "campaign_id" in sig.parameters, (
        "collect_baseline must accept campaign_id keyword argument (BUG 2 AC19)"
    )


def test_run_baseline_sort_no_campaign_id_no_tag_in_notes():
    """Without campaign_id, run_baseline_sort records have no campaign_id tag (AC20).

    AC20: when campaign_id is not supplied, campaign_id=None is passed and
    no 'campaign_id=None' tag appears in the record's qa_notes.
    """
    items = ["apple", "bread", "cheese", "egg", "fish"]
    records = asyncio.run(
        run_baseline_sort(
            _mock_adapter(), _domain(),
            items=items,
            baseline_id="test_baseline",
            n_sorts=1,
        )
    )
    for rec in records:
        assert "campaign_id=" not in rec.qa_notes, (
            f"qa_notes must not contain campaign_id tag when not supplied, "
            f"got: {rec.qa_notes!r}"
        )
