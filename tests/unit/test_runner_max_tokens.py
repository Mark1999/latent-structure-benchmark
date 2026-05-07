"""Unit tests: InformantRecord.max_tokens records the actual per-call value.

Verifies that runner._assemble_record() stores max_tokens from
AdapterResult.max_tokens_used rather than any hardcoded constant.

Fix-forward task: sibling to Phase 4b T2 (commit 628497d).
Reviewer-T2 finding: docs/status/2026-05-07-phase4b-t2-reviewer-verdict.md note 1.
"""

import asyncio
import json
from datetime import date
from unittest.mock import MagicMock

from cdb_collect.adapters.base import AdapterResult
from cdb_collect.runner import run_baseline_sort, run_informant
from cdb_core import Domain, ModelRef

# ─── Shared fixtures ─────────────────────────────────────────────────


def _model_ref(collection_method: str = "anthropic_api") -> ModelRef:
    return ModelRef(
        provider="anthropic",
        model_id="claude-opus-4-6",
        family="claude",
        origin="us",
        open_weights=False,
        collection_method=collection_method,
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


def _free_list_result(max_tokens_used: int = 4096) -> AdapterResult:
    text = (
        "1. Mother\n2. Father\n3. Sister\n4. Brother\n5. Aunt\n"
        "6. Uncle\n7. Grandmother\n8. Grandfather\n9. Cousin\n10. Niece"
    )
    return AdapterResult(
        text=text,
        raw_response={"id": "msg_free"},
        latency_ms=350,
        input_tokens=87,
        output_tokens=30,
        provider_request_id="msg_free_123",
        model_version_returned="claude-opus-4-6-20260401",
        stop_reason="end_turn",
        max_tokens_used=max_tokens_used,
    )


def _pile_sort_result(max_tokens_used: int = 4096) -> AdapterResult:
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
        raw_response={"id": "msg_sort"},
        latency_ms=400,
        input_tokens=120,
        output_tokens=50,
        provider_request_id="msg_sort_123",
        model_version_returned="claude-opus-4-6-20260401",
        stop_reason="end_turn",
        max_tokens_used=max_tokens_used,
    )


def _interview_result() -> AdapterResult:
    text = "1. Parents\n2. Siblings\n3. Aunts and Uncles\n4. Extended family"
    return AdapterResult(
        text=text,
        raw_response={"id": "msg_int"},
        latency_ms=200,
        input_tokens=80,
        output_tokens=20,
        provider_request_id="msg_int_123",
        model_version_returned="claude-opus-4-6-20260401",
        stop_reason="end_turn",
    )


def _mock_adapter_with_max_tokens(
    freelist_max_tokens: int = 4096,
    pilesort_max_tokens: int = 4096,
) -> MagicMock:
    """Mock adapter that returns AdapterResult with the given max_tokens_used values."""
    adapter = MagicMock()
    adapter.model = _model_ref()

    async def mock_complete(prompt, *, json_schema=None, temperature=0.7):
        lower = prompt.lower()
        if "label" in lower or "organizing principle" in lower:
            return _interview_result()
        elif "sort" in lower:
            return _pile_sort_result(max_tokens_used=pilesort_max_tokens)
        else:
            return _free_list_result(max_tokens_used=freelist_max_tokens)

    adapter.complete = mock_complete
    return adapter


# ─── Tests ────────────────────────────────────────────────────────────


def test_run_informant_records_actual_max_tokens_not_hardcoded_4096():
    """InformantRecord.max_tokens reflects AdapterResult.max_tokens_used.

    When an adapter sends max_tokens=16384, the assembled InformantRecord
    must store 16384, not the old hardcoded constant 4096.

    This is the primary regression test for the fix-forward metadata
    accuracy task (Reviewer-T2 finding, note 1).
    """
    adapter = _mock_adapter_with_max_tokens(
        freelist_max_tokens=16384,
        pilesort_max_tokens=16384,
    )
    record = asyncio.run(run_informant(adapter, _domain(), 0))

    assert record.max_tokens == 16384, (
        f"Expected max_tokens=16384 (actual API cap), got {record.max_tokens}. "
        "runner.py must read AdapterResult.max_tokens_used, not hardcode 4096."
    )


def test_run_informant_records_adaptive_max_tokens_phi4_style():
    """InformantRecord.max_tokens reflects an adaptive per-call value (~13872 phi-4 style).

    Models with a small context window produce an effective max_tokens below
    the global cap. The runner must record that per-call value.
    """
    phi4_effective_cap = 13872  # compute_effective_max_tokens("~2K prompt", 16384)
    adapter = _mock_adapter_with_max_tokens(
        freelist_max_tokens=phi4_effective_cap,
        pilesort_max_tokens=phi4_effective_cap,
    )
    record = asyncio.run(run_informant(adapter, _domain(), 0))

    assert record.max_tokens == phi4_effective_cap, (
        f"Expected max_tokens={phi4_effective_cap} (adaptive phi-4 style cap), "
        f"got {record.max_tokens}."
    )


def test_run_informant_default_adapter_result_preserves_4096():
    """When AdapterResult.max_tokens_used defaults to 4096, InformantRecord stores 4096.

    Ensures backward-compatibility: test fixtures that do not set max_tokens_used
    produce an InformantRecord with max_tokens=4096 rather than crashing.
    """
    adapter = _mock_adapter_with_max_tokens(
        freelist_max_tokens=4096,
        pilesort_max_tokens=4096,
    )
    record = asyncio.run(run_informant(adapter, _domain(), 0))

    assert record.max_tokens == 4096


def test_baseline_sort_records_actual_max_tokens():
    """run_baseline_sort also records the adapter's actual max_tokens.

    In baseline_sort mode, the ps_result is passed as the 'freelist_result'
    argument to _assemble_record. Verifies this path also propagates correctly.
    """
    adapter = _mock_adapter_with_max_tokens(
        freelist_max_tokens=4096,
        pilesort_max_tokens=16384,  # pile sort result carries the real cap
    )
    items = ["mother", "father", "sister", "brother", "aunt"]
    records = asyncio.run(
        run_baseline_sort(
            adapter, _domain(),
            items=items, baseline_id="romney_1996", n_sorts=1,
        )
    )
    assert len(records) == 1
    # In baseline_sort, ps_result (max_tokens_used=16384) is passed as
    # freelist_result to _assemble_record, so the record should carry 16384.
    assert records[0].max_tokens == 16384, (
        f"Expected max_tokens=16384 from ps_result path, got {records[0].max_tokens}."
    )
