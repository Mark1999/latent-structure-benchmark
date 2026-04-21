"""Tests for T07 (honest qa_passed) and T09 (label-count mismatch FAIL-and-record).

T07: runner._assemble_record must wire check_record() return to qa_passed instead
     of hardcoding True. qa_notes must include both failure reasons and campaign_id.

T09: pile_interview.parse_pile_interview returns a structured mismatch signal
     instead of raising. The assembled InformantRecord gets qa_passed=False and
     qa_notes containing 'label_count_mismatch:N/M'.

See docs/status/2026-04-20-f2-cda-sme-verdict.md §T07 and §T09.
"""

from __future__ import annotations

import asyncio
import json
from datetime import date, datetime
from unittest.mock import MagicMock

from cdb_collect.adapters.base import AdapterResult
from cdb_collect.protocol.pile_interview import parse_pile_interview
from cdb_collect.runner import run_informant
from cdb_core import (
    Domain,
    FreelistRecord,
    InformantRecord,
    InterviewRecord,
    ModelRef,
    PileSortRecord,
)

from scripts.qa_check import check_8_label_count_match, run_qa_checks

# ─── Shared fixtures ────────────────────────────────────────────────────────


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


def _free_list_10_items() -> AdapterResult:
    """10 items — passes check_1 (MIN_FREELIST_ITEMS=10)."""
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


def _free_list_few_items() -> AdapterResult:
    """Only 2 items — deliberately fails check_1 (MIN_FREELIST_ITEMS=10)."""
    text = "1. Mother\n2. Father"
    return AdapterResult(
        text=text,
        raw_response={"id": "msg_free_few", "content": [{"text": text}]},
        latency_ms=350,
        cost_usd=0.01,
        input_tokens=87,
        output_tokens=10,
        provider_request_id="msg_free_few_123",
        model_version_returned="claude-opus-4-6-20260401",
        stop_reason="end_turn",
    )


def _pile_sort_4_piles() -> AdapterResult:
    """4 piles covering all 10 items — valid for check_3/4/8."""
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


def _interview_4_labels() -> AdapterResult:
    """4 labels — matches 4 piles; check_8 passes."""
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


def _interview_3_labels() -> AdapterResult:
    """3 labels — mismatches 4 piles; check_8 must fire."""
    text = "1. Parents\n2. Siblings\n3. Extended family"
    return AdapterResult(
        text=text,
        raw_response={"id": "msg_int_short", "content": [{"text": text}]},
        latency_ms=200,
        cost_usd=0.005,
        input_tokens=80,
        output_tokens=15,
        provider_request_id="msg_int_short_123",
        model_version_returned="claude-opus-4-6-20260401",
        stop_reason="end_turn",
    )


def _mock_adapter_all_pass() -> MagicMock:
    """Mock adapter producing a fully-passing record (10 items, 4 piles, 4 labels)."""
    adapter = MagicMock()
    adapter.model = _model_ref()

    async def mock_complete(prompt, *, json_schema=None, temperature=0.7):
        lower = prompt.lower()
        if "label" in lower or "organizing principle" in lower:
            return _interview_4_labels()
        elif "sort" in lower:
            return _pile_sort_4_piles()
        else:
            return _free_list_10_items()

    adapter.complete = mock_complete
    return adapter


def _mock_adapter_failing_freelist() -> MagicMock:
    """Mock adapter producing a record that fails check_1 (only 2 free-list items)."""
    adapter = MagicMock()
    adapter.model = _model_ref()

    async def mock_complete(prompt, *, json_schema=None, temperature=0.7):
        lower = prompt.lower()
        if "label" in lower or "organizing principle" in lower:
            text = "1. Parents\n2. Immediate family"
            return AdapterResult(
                text=text,
                raw_response={"id": "msg_int2", "content": [{"text": text}]},
                latency_ms=200, cost_usd=0.005,
                input_tokens=80, output_tokens=15,
                provider_request_id="msg_int2_123",
                model_version_returned="claude-opus-4-6-20260401",
                stop_reason="end_turn",
            )
        elif "sort" in lower:
            piles_json = json.dumps({"piles": [["mother"], ["father"]]})
            return AdapterResult(
                text=piles_json,
                raw_response={"id": "msg_sort2", "content": [{"text": piles_json}]},
                latency_ms=400, cost_usd=0.02,
                input_tokens=120, output_tokens=50,
                provider_request_id="msg_sort2_123",
                model_version_returned="claude-opus-4-6-20260401",
                stop_reason="end_turn",
            )
        else:
            return _free_list_few_items()

    adapter.complete = mock_complete
    return adapter


def _mock_adapter_label_mismatch() -> MagicMock:
    """Mock adapter where interview returns 3 labels for 4 piles (check_8 failure)."""
    adapter = MagicMock()
    adapter.model = _model_ref()

    async def mock_complete(prompt, *, json_schema=None, temperature=0.7):
        lower = prompt.lower()
        if "label" in lower or "organizing principle" in lower:
            return _interview_3_labels()  # 3 labels, but 4 piles
        elif "sort" in lower:
            return _pile_sort_4_piles()  # 4 piles
        else:
            return _free_list_10_items()  # 10 items (check_1 passes)

    adapter.complete = mock_complete
    return adapter


# ─── T07: Honest qa_passed ───────────────────────────────────────────────────


class TestT07HonestQaPassed:
    def test_passing_record_has_qa_passed_true(self):
        """All checks pass → qa_passed=True and qa_notes is empty (no campaign_id)."""
        record = asyncio.run(run_informant(_mock_adapter_all_pass(), _domain(), 0))
        assert record.qa_passed is True
        assert record.qa_notes == ""

    def test_failing_record_has_qa_passed_false(self):
        """check_1 fails (2 items < 10) → qa_passed=False."""
        record = asyncio.run(
            run_informant(_mock_adapter_failing_freelist(), _domain(), 0)
        )
        assert record.qa_passed is False

    def test_failing_record_qa_notes_contains_failure_reason(self):
        """When check_1 fails, qa_notes includes the failure actual string."""
        record = asyncio.run(
            run_informant(_mock_adapter_failing_freelist(), _domain(), 0)
        )
        assert record.qa_notes != ""

    def test_passing_record_with_campaign_id(self):
        """All checks pass + campaign_id → qa_passed=True, qa_notes='campaign_id=...'."""
        record = asyncio.run(
            run_informant(
                _mock_adapter_all_pass(), _domain(), 0,
                campaign_id="shakedown-20260420",
            )
        )
        assert record.qa_passed is True
        assert record.qa_notes == "campaign_id=shakedown-20260420"

    def test_failing_record_with_campaign_id_preserves_campaign_tag(self):
        """Failure notes AND campaign_id tag both appear in qa_notes."""
        record = asyncio.run(
            run_informant(
                _mock_adapter_failing_freelist(), _domain(), 0,
                campaign_id="shakedown-20260420",
            )
        )
        assert record.qa_passed is False
        assert "campaign_id=shakedown-20260420" in record.qa_notes


# ─── T09: Label-count mismatch FAIL-and-record ───────────────────────────────


class TestT09LabelCountMismatch:
    def test_parser_mismatch_returns_structured_signal_not_raises(self):
        """21 piles + 20 labels → parse_pile_interview returns mismatch signal."""
        text = "\n".join(f"{i}. Label {i}" for i in range(1, 21))
        result = parse_pile_interview(text, expected_count=21)
        assert result.label_count_mismatch == (21, 20)
        assert len(result.labels) == 20

    def test_parser_mismatch_preserves_raw_labels(self):
        """The partial labels are preserved exactly as parsed (no padding)."""
        text = "1. Nuclear family\n2. Extended family"
        result = parse_pile_interview(text, expected_count=3)
        assert result.labels == ["Nuclear family", "Extended family"]
        assert result.label_count_mismatch == (3, 2)

    def test_parser_match_has_no_mismatch_signal(self):
        """Matched count → label_count_mismatch is None."""
        text = "1. Nuclear family\n2. Extended family\n3. In-laws"
        result = parse_pile_interview(text, expected_count=3)
        assert result.label_count_mismatch is None
        assert len(result.labels) == 3

    def test_assembled_record_label_mismatch_qa_passed_false(self):
        """4 piles + 3 labels → qa_passed=False and qa_notes includes mismatch token."""
        record = asyncio.run(
            run_informant(_mock_adapter_label_mismatch(), _domain(), 0)
        )
        assert record.qa_passed is False
        assert "label_count_mismatch" in record.qa_notes

    def test_assembled_record_label_mismatch_notes_format(self):
        """qa_notes contains 'label_count_mismatch:4/3' for 4 piles / 3 labels."""
        record = asyncio.run(
            run_informant(_mock_adapter_label_mismatch(), _domain(), 0)
        )
        assert "label_count_mismatch:4/3" in record.qa_notes

    def test_assembled_record_label_mismatch_raw_response_preserved(self):
        """interview.response_verbatim is intact even when labels mismatch piles."""
        record = asyncio.run(
            run_informant(_mock_adapter_label_mismatch(), _domain(), 0)
        )
        assert "Parents" in record.interview.response_verbatim

    def test_matched_count_record_passes_check_8(self):
        """4 piles + 4 labels → check_8 passes; qa_passed=True (all checks pass)."""
        record = asyncio.run(run_informant(_mock_adapter_all_pass(), _domain(), 0))
        assert record.qa_passed is True
        assert "label_count_mismatch" not in record.qa_notes

    def test_empty_label_does_not_trigger_false_positive(self):
        """Count-based check: an empty-string label counts toward the total.

        The check is count-based, not content-based. This test confirms the
        check fires only on count divergence, not label content.
        """
        pile_sort = PileSortRecord(
            prompt_verbatim="p", prompt_version="v1",
            response_verbatim="r", response_object_json={},
            input_tokens=1, output_tokens=1, latency_ms=1,
            stop_reason="end_turn",
            parsed_piles=[["a", "b"], ["c"], ["d"]],
            parsed_matrix=[[1, 1, 0, 0], [1, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
        )
        interview = InterviewRecord(
            prompt_verbatim="p", prompt_version="v1",
            response_verbatim="r", response_object_json={},
            input_tokens=1, output_tokens=1, latency_ms=1,
            stop_reason="end_turn",
            parsed_pile_labels=["Group A", "", "Group C"],  # empty string still counts
        )
        record = _make_record_with_steps(pile_sort=pile_sort, interview=interview)
        failure = check_8_label_count_match(record)
        assert failure is None, (
            f"check_8 should not fire when counts match (3 piles, 3 labels); got: {failure}"
        )


# ─── T09: check_8_label_count_match unit tests ──────────────────────────────


class TestCheck8LabelCountMatch:
    """Unit tests for check_8_label_count_match in isolation."""

    def test_skips_when_pile_sort_not_collected(self):
        """Placeholder pile sort → check skipped (returns None)."""
        record = _make_minimal_record(
            pile_sort_stop="not_collected", interview_stop="not_collected",
        )
        assert check_8_label_count_match(record) is None

    def test_skips_when_interview_not_collected(self):
        """Placeholder interview → check skipped (returns None)."""
        record = _make_minimal_record(
            pile_stop="end_turn", interview_stop="not_collected",
            n_piles=3, n_labels=0,
        )
        assert check_8_label_count_match(record) is None

    def test_returns_failure_when_counts_differ(self):
        """4 piles / 3 labels → QAFailure with check_num=8."""
        record = _make_minimal_record(n_piles=4, n_labels=3)
        failure = check_8_label_count_match(record)
        assert failure is not None
        assert failure.check_num == 8
        assert "label_count_mismatch:4/3" in failure.actual

    def test_returns_none_when_counts_match(self):
        """4 piles / 4 labels → no failure."""
        record = _make_minimal_record(n_piles=4, n_labels=4)
        assert check_8_label_count_match(record) is None

    def test_failure_included_in_run_qa_checks(self):
        """check_8 must be part of the run_qa_checks battery."""
        record = _make_minimal_record(n_piles=4, n_labels=3)
        failures = run_qa_checks(record)
        check_nums = {f.check_num for f in failures}
        assert 8 in check_nums


# ─── Helpers ────────────────────────────────────────────────────────────────


_MANIFEST = {k: "a" * 64 for k in [
    "freelist_prompt", "freelist_response",
    "pilesort_prompt", "pilesort_response",
    "interview_prompt", "interview_response",
    "request_params", "informant_record_total",
]}

_BASE_KWARGS: dict = dict(
    informant_id="test_rec",
    domain_slug="family",
    run_index=0,
    collection_date=datetime(2026, 4, 21),
    model_id="claude-opus-4-6",
    model_version_returned="claude-opus-4-6-20260401",
    family="claude",
    provider="anthropic",
    provider_request_id="req_test",
    knowledge_cutoff=None,
    open_weights=False,
    origin_country="us",
    alignment_method=None,
    collection_method="anthropic_api",
    api_endpoint="https://api.anthropic.com/v1/messages",
    api_version="",
    temperature=0.7,
    top_p=None,
    max_tokens=16384,
    system_prompt="",
    sha256_manifest=_MANIFEST,
    qa_passed=True,
)

_PLACEHOLDER_FL = FreelistRecord(
    prompt_verbatim="p", prompt_version="v1",
    response_verbatim="r", response_object_json={},
    input_tokens=1, output_tokens=1, latency_ms=1,
    stop_reason="not_collected",
    parsed_items=[], parsed_raw_order=[],
)


def _make_record_with_steps(
    pile_sort: PileSortRecord,
    interview: InterviewRecord,
) -> InformantRecord:
    """Assemble a minimal InformantRecord with explicit step records."""
    return InformantRecord(
        **_BASE_KWARGS,
        freelist=_PLACEHOLDER_FL,
        pile_sort=pile_sort,
        interview=interview,
    )


def _make_minimal_record(
    n_piles: int = 3,
    n_labels: int = 3,
    pile_stop: str = "end_turn",
    pile_sort_stop: str | None = None,
    interview_stop: str = "end_turn",
) -> InformantRecord:
    """Build a minimal InformantRecord for check_8 unit testing."""
    effective_pile_stop = pile_sort_stop if pile_sort_stop is not None else pile_stop
    piles = [["item"] for _ in range(n_piles)]
    labels = [f"label_{i}" for i in range(n_labels)]

    pile_sort = PileSortRecord(
        prompt_verbatim="p", prompt_version="v1",
        response_verbatim="r", response_object_json={},
        input_tokens=1, output_tokens=1, latency_ms=1,
        stop_reason=effective_pile_stop,
        parsed_piles=piles if effective_pile_stop != "not_collected" else [],
        parsed_matrix=[[1]],
    )
    interview = InterviewRecord(
        prompt_verbatim="p", prompt_version="v1",
        response_verbatim="r", response_object_json={},
        input_tokens=1, output_tokens=1, latency_ms=1,
        stop_reason=interview_stop,
        parsed_pile_labels=labels if interview_stop != "not_collected" else [],
    )
    return _make_record_with_steps(pile_sort=pile_sort, interview=interview)
