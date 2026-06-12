"""Tests for transport-failure record append at per-model boundary (BUG 3).

Verifies that when the adapter raises during cross-model or single-pass
collection, a failure record is appended to failures.jsonl with the
correct context fields.

All tests use mock adapters and temp files. No real API calls.

CDA SME binding notes applied:
- C1: log messages use 'the adapter raised' / 'LSB recorded'; no model-attribution
  language ('the model failed/refused/crashed') in any string checked here.
- C2: context['failure_scope']='per_model' is the chosen key (not model_level=True)
  for unambiguous LSB-event-scoping at the model-level boundary.
- C3: anti-attribution sentence in commit body (not in this file).
- C4: response_verbatim is absent from failure records when the response did not
  arrive (absence-is-signal; jsonl.py L112 correctly omits the field when None).
"""

from __future__ import annotations

import asyncio
import json
from datetime import date, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

from cdb_collect.adapters.base import AdapterResult
from cdb_core import (
    Domain,
    FreelistRecord,
    InformantRecord,
    InterviewRecord,
    ModelRef,
    PileSortRecord,
)


def _model_ref(model_id: str = "test/mock-transport-fail") -> ModelRef:
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


def _mock_adapter_transport_fail(
    model_id: str = "test/mock-fail",
    error_msg: str = "400 Bad Request: provider rejected the request",
) -> MagicMock:
    """Adapter that always raises a transport error on complete()."""
    adapter = MagicMock()
    adapter.model = _model_ref(model_id)

    async def mock_complete(prompt, *, json_schema=None, temperature=0.7):
        raise ConnectionError(error_msg)

    adapter.complete = mock_complete
    return adapter


def _mock_adapter_ok(model_id: str = "test/mock-ok") -> MagicMock:
    """Adapter that always succeeds."""
    adapter = MagicMock()
    adapter.model = _model_ref(model_id)

    async def mock_complete(prompt, *, json_schema=None, temperature=0.7):
        import json as _json
        lower = prompt.lower()
        if "label" in lower or "organizing principle" in lower:
            text = "1. Fruits\n2. Staples"
            return AdapterResult(
                text=text, raw_response={}, latency_ms=100,
                input_tokens=60, output_tokens=15,
                provider_request_id="mock-iv",
                model_version_returned=model_id + "-v1",
                stop_reason="end_turn",
            )
        piles = _json.dumps({"piles": [["apple", "grape"], ["bread", "cheese"]]})
        return AdapterResult(
            text=piles, raw_response={}, latency_ms=100,
            input_tokens=80, output_tokens=40,
            provider_request_id="mock-ps",
            model_version_returned=model_id + "-v1",
            stop_reason="end_turn",
        )

    adapter.complete = mock_complete
    return adapter


def _make_minimal_record(model_id: str) -> InformantRecord:
    """Minimal valid InformantRecord for mocking run_cross_model_sort returns."""
    return InformantRecord(
        informant_id="test_" + model_id.replace("/", "_"),
        domain_slug="food",
        run_index=0,
        collection_date=datetime(2026, 6, 12),
        model_id=model_id,
        model_version_returned=model_id + "-v1",
        family="mock",
        provider="openrouter",
        provider_request_id="mock",
        knowledge_cutoff=None,
        open_weights=False,
        origin_country="us",
        alignment_method=None,
        collection_method="openrouter",
        api_endpoint="https://openrouter.ai/api/v1/chat/completions",
        api_version="",
        temperature=0.3,
        top_p=None,
        max_tokens=16384,
        system_prompt="",
        freelist=FreelistRecord(
            prompt_verbatim="", prompt_version="v1",
            response_verbatim="", response_object_json={},
            input_tokens=0, output_tokens=0, latency_ms=0,
            stop_reason="not_collected",
            parsed_items=[], parsed_raw_order=[],
        ),
        pile_sort=PileSortRecord(
            prompt_verbatim="", prompt_version="v1",
            response_verbatim="", response_object_json={},
            input_tokens=0, output_tokens=0, latency_ms=0,
            stop_reason="end_turn",
            parsed_piles=[["apple"], ["bread"]],
            parsed_matrix=[[1, 0], [0, 1]],
            item_source="cross_model_consensus",
        ),
        interview=InterviewRecord(
            prompt_verbatim="", prompt_version="v1",
            response_verbatim="", response_object_json={},
            input_tokens=0, output_tokens=0, latency_ms=0,
            stop_reason="end_turn",
            parsed_pile_labels=["Fruits", "Staples"],
        ),
        sha256_manifest={k: "a" * 64 for k in [
            "freelist_prompt", "freelist_response",
            "pilesort_prompt", "pilesort_response",
            "interview_prompt", "interview_response",
            "request_params", "informant_record_total",
        ]},
        qa_passed=True,
        qa_notes="",
    )


# ── BUG 3 AC16+17+21: cross_model transport failure appends to failures.jsonl ─


def test_cross_model_transport_failure_appended_to_failures_jsonl(tmp_path: Path):
    """When the adapter raises during cross_model sort, a failure record is appended.

    This exercises the per-model boundary in collect_cross_model:
      except Exception as e:
          append_failure(e, {..., 'failure_scope': 'per_model'}, FAILURES_JSONL)
          continue

    LSB's detection of a provider-transport event (the adapter raised) is recorded
    in failures.jsonl; no output from the model arrived. The record must not
    attribute intent or behavior to the model itself per CDA SME C1.
    """
    from scripts.collect import collect_cross_model

    failures_path = tmp_path / "failures.jsonl"
    informants_path = tmp_path / "informants.jsonl"

    fail_adapter = _mock_adapter_transport_fail("test/fail-model", "400 Bad Request")
    ok_adapter = _mock_adapter_ok("test/ok-model")

    error_msg = "400 Bad Request"

    async def mock_rcs(adapter, domain, *, consensus_items, n_pile_sorts,
                       prompt_version, campaign_id=None):
        if adapter.model.model_id == "test/fail-model":
            raise ConnectionError(error_msg)
        return [_make_minimal_record(adapter.model.model_id)]

    # Pre-create informants.jsonl using the fixture record as a valid free-list base.
    # collect_cross_model reads the file and calls InformantRecord(**rec_dict), so
    # we need a fully valid record. We use the fixture record and override model_id
    # and domain_slug so collect_cross_model populates records_by_model correctly.
    _fixtures = Path(__file__).resolve().parents[1] / "fixtures"
    fixture_lines = (
        _fixtures / "open_bundle_informants_fixture.jsonl"
    ).read_text(encoding="utf-8").splitlines()
    base_rec = json.loads(fixture_lines[0])
    base_rec["model_id"] = "test/ok-model"
    base_rec["domain_slug"] = "food"
    # Ensure freelist.output_tokens > 0 so collect_cross_model includes this record
    base_rec["freelist"]["output_tokens"] = 10
    # Fixture may have legacy truncation_type="none" (pre-v0.7 string); normalize to null
    if base_rec.get("truncation_type") == "none":
        base_rec["truncation_type"] = None
    informants_path.write_text(json.dumps(base_rec) + "\n", encoding="utf-8")

    # compute_cross_model_consensus and find_salience_elbow are imported inside
    # collect_cross_model's function body from cdb_analyze.consensus, so they
    # must be patched at their source module, not at scripts.collect.
    with (
        patch("scripts.collect.FAILURES_JSONL", failures_path),
        patch("scripts.collect.run_cross_model_sort", side_effect=mock_rcs),
        patch(
            "cdb_analyze.consensus.compute_cross_model_consensus",
            return_value=[("apple", 0.9), ("bread", 0.7)],
        ),
        patch("cdb_analyze.consensus.find_salience_elbow", return_value=2),
    ):
        result = asyncio.run(
            collect_cross_model(
                [fail_adapter, ok_adapter],
                "food", 1, informants_path,
            )
        )

    # The ok_adapter produced 1 record; fail_adapter was skipped via continue
    assert result == 1

    # Exactly one failure line was written
    assert failures_path.exists(), "failures.jsonl must be created on transport failure"
    lines = [ln for ln in failures_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 1, f"Expected exactly 1 failure line, got {len(lines)}"

    entry = json.loads(lines[0])
    assert entry["error_type"] == "ConnectionError"
    assert error_msg in entry["error_message"]

    ctx = entry["context"]
    assert ctx["model_id"] == "test/fail-model"
    assert ctx["domain"] == "food"
    assert ctx["mode"] == "cross_model_consensus"
    # SME C2: failure_scope="per_model" distinguishes model-level transport events
    assert ctx["failure_scope"] == "per_model", (
        "context must contain failure_scope='per_model' per CDA SME C2"
    )


def test_cross_model_continues_past_failed_model(tmp_path: Path):
    """After one model's adapter raises, collection continues for subsequent models.

    AC23: cross_model collection continues past the failed model. The fix is
    only the failure-record append; the loop continuation was pre-existing.
    """
    from scripts.collect import collect_cross_model

    failures_path = tmp_path / "failures.jsonl"
    informants_path = tmp_path / "informants.jsonl"

    fail_adapter = _mock_adapter_transport_fail("test/fail-model")
    ok_adapter_1 = _mock_adapter_ok("test/ok-model-1")
    ok_adapter_2 = _mock_adapter_ok("test/ok-model-2")

    async def mock_rcs(adapter, domain, *, consensus_items, n_pile_sorts,
                       prompt_version, campaign_id=None):
        if adapter.model.model_id == "test/fail-model":
            raise ConnectionError("400 Bad Request")
        return [_make_minimal_record(adapter.model.model_id)]

    _fixtures = Path(__file__).resolve().parents[1] / "fixtures"
    fixture_lines = (
        _fixtures / "open_bundle_informants_fixture.jsonl"
    ).read_text(encoding="utf-8").splitlines()
    base_rec = json.loads(fixture_lines[0])
    base_rec["model_id"] = "test/ok-model-1"
    base_rec["domain_slug"] = "food"
    base_rec["freelist"]["output_tokens"] = 10
    if base_rec.get("truncation_type") == "none":
        base_rec["truncation_type"] = None
    informants_path.write_text(json.dumps(base_rec) + "\n", encoding="utf-8")

    with (
        patch("scripts.collect.FAILURES_JSONL", failures_path),
        patch("scripts.collect.run_cross_model_sort", side_effect=mock_rcs),
        patch(
            "cdb_analyze.consensus.compute_cross_model_consensus",
            return_value=[("apple", 0.9), ("bread", 0.7)],
        ),
        patch("cdb_analyze.consensus.find_salience_elbow", return_value=2),
    ):
        result = asyncio.run(
            collect_cross_model(
                [fail_adapter, ok_adapter_1, ok_adapter_2],
                "food", 1, informants_path,
            )
        )

    # 2 ok models produced records despite 1 failure
    assert result == 2, (
        f"Expected 2 records from 2 ok models, got {result}. "
        "Loop must continue past the failed model."
    )


# ── BUG 3 AC22: single_pass transport failure appends to failures.jsonl ───────


def test_single_pass_transport_failure_appended_to_failures_jsonl(tmp_path: Path):
    """When the adapter raises during single_pass, a failure record is appended.

    LSB records the provider-transport event (the adapter raised). The failure
    record preserves the error verbatim per the failures-are-findings principle
    (CLAUDE.md memory project_failures_are_findings.md). No response_verbatim
    is written when no response arrived (CDA SME C4).
    """
    from scripts.collect import collect_single_pass

    failures_path = tmp_path / "failures.jsonl"
    informants_path = tmp_path / "informants.jsonl"

    error_msg = "500 Internal Server Error: upstream provider unavailable"
    fail_adapter = _mock_adapter_transport_fail("test/single-fail", error_msg)

    with (
        patch("scripts.collect.FAILURES_JSONL", failures_path),
        patch(
            "scripts.collect.run_informant",
            side_effect=Exception(error_msg),
        ),
    ):
        result = asyncio.run(
            collect_single_pass(
                fail_adapter, "food", 1, informants_path,
            )
        )

    # Returned 0 successes
    assert result == 0

    # Exactly one failure line was written
    assert failures_path.exists()
    lines = [ln for ln in failures_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 1, f"Expected 1 failure line, got {len(lines)}"

    entry = json.loads(lines[0])
    assert error_msg in entry["error_message"]
    assert entry["context"]["model_id"] == "test/single-fail"
    assert entry["context"]["domain"] == "food"
    # response_verbatim should be absent when no response arrived (C4)
    assert "response_verbatim" not in entry, (
        "response_verbatim must be absent when no response arrived (CDA SME C4)"
    )
