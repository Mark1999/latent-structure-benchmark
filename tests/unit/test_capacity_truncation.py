"""Tests for InformantRecord capacity-constrained truncation fields.

See docs/SME_REVIEW.md §1.7 and docs/DATA_DICTIONARY.md §1.1 /
"Capacity-constrained truncation" subsection.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from cdb_core import (
    FreelistRecord,
    InformantRecord,
    InterviewRecord,
    PileSortRecord,
)


def _base_kwargs() -> dict:
    """Minimum InformantRecord kwargs; capacity fields defaulted."""
    return dict(
        informant_id="cap_test",
        domain_slug="family",
        run_index=0,
        collection_date=datetime(2026, 4, 19, tzinfo=UTC),
        model_id="m",
        model_version_returned="m-v1",
        family="test",
        provider="anthropic",
        provider_request_id="req",
        knowledge_cutoff=None,
        open_weights=False,
        origin_country="us",
        alignment_method=None,
        collection_method="anthropic_api",
        api_endpoint="https://x",
        api_version="v1",
        temperature=0.7,
        top_p=None,
        max_tokens=16384,
        system_prompt="s",
        freelist=FreelistRecord(
            prompt_verbatim="p", prompt_version="v1", response_verbatim="r",
            response_object_json={}, input_tokens=1, output_tokens=1,
            latency_ms=1, stop_reason="end_turn",
            parsed_items=["a"], parsed_raw_order=["a"],
        ),
        pile_sort=PileSortRecord(
            prompt_verbatim="p", prompt_version="v1", response_verbatim="r",
            response_object_json={}, input_tokens=1, output_tokens=1,
            latency_ms=1, stop_reason="end_turn",
            parsed_piles=[["a"]], parsed_matrix=[[1]],
        ),
        interview=InterviewRecord(
            prompt_verbatim="p", prompt_version="v1", response_verbatim="r",
            response_object_json={}, input_tokens=1, output_tokens=1,
            latency_ms=1, stop_reason="end_turn",
            parsed_pile_labels=["pile_0"],
        ),
        sha256_manifest={
            "freelist_prompt": "a", "freelist_response": "b",
            "pilesort_prompt": "c", "pilesort_response": "d",
            "interview_prompt": "e", "interview_response": "f",
            "request_params": "g", "informant_record_total": "h",
        },
        qa_passed=True,
    )


class TestCapacityTruncationDefaults:
    def test_all_capacity_fields_optional(self):
        """A record without any capacity fields must still validate."""
        rec = InformantRecord(**_base_kwargs())
        assert rec.truncation_type is None
        assert rec.truncation_n is None
        assert rec.max_possible_n is None
        assert rec.context_window_exceeded is False
        assert rec.capacity_note == ""

    def test_context_window_exceeded_does_not_fail_qa(self):
        """context_window_exceeded=True is a finding, not a QA failure.

        Per docs/SME_REVIEW.md §1.7: a record with
        context_window_exceeded=True can still have qa_passed=True. The
        schema does not couple these fields; the QA_Runner's six
        deterministic checks live in scripts/qa_check.py and none of
        them gate on context_window_exceeded.
        """
        rec = InformantRecord(
            **_base_kwargs(),
            context_window_exceeded=True,
            capacity_note="model returned 487 items before context limit at step 2",
        )
        assert rec.qa_passed is True
        assert rec.context_window_exceeded is True

    def test_truncation_type_enum_literals(self):
        for t in ("elbow", "capacity", "prompt_ceiling", "context_window_exceeded"):
            rec = InformantRecord(
                **_base_kwargs(),
                truncation_type=t,
                truncation_n=42,
            )
            assert rec.truncation_type == t

    def test_invalid_truncation_type_rejected(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            InformantRecord(**_base_kwargs(), truncation_type="bogus")

    def test_max_possible_n_can_be_null(self):
        rec = InformantRecord(
            **_base_kwargs(),
            truncation_type="prompt_ceiling",
            truncation_n=30,
            max_possible_n=None,
        )
        assert rec.max_possible_n is None
