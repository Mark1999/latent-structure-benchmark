"""Integration test for the analysis pipeline. Uses synthetic records."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from cdb_analyze.pipeline import (
    group_by_model,
    load_records,
    run_pipeline,
    write_result,
)
from cdb_core import (
    FreelistRecord,
    InformantRecord,
    InterviewRecord,
    PileSortRecord,
)


def _make_record(
    model_id: str,
    run_index: int,
    items: list[str],
    piles: list[list[str]],
) -> InformantRecord:
    """Build a minimal InformantRecord."""
    n = len(items)
    matrix = [[0] * n for _ in range(n)]
    idx = {item: i for i, item in enumerate(items)}
    for pile in piles:
        for a in pile:
            for b in pile:
                matrix[idx[a]][idx[b]] = 1

    return InformantRecord(
        informant_id=f"{model_id}_{run_index}",
        domain_slug="family",
        run_index=run_index,
        collection_date=datetime(2026, 4, 13, tzinfo=UTC),
        model_id=model_id,
        model_version_returned=f"{model_id}-v1",
        family="test",
        provider="anthropic",
        provider_request_id=f"req_{run_index}",
        knowledge_cutoff=None,
        open_weights=False,
        origin_country="us",
        alignment_method=None,
        collection_method="anthropic_api",
        api_endpoint="https://api.anthropic.com/v1/messages",
        api_version="2023-06-01",
        temperature=0.7,
        top_p=None,
        max_tokens=16384,
        system_prompt="test",
        freelist=FreelistRecord(
            prompt_verbatim="test",
            prompt_version="v1",
            response_verbatim="test",
            response_object_json={},
            input_tokens=50,
            output_tokens=20,
            latency_ms=1000,
            stop_reason="end_turn",
            parsed_items=items,
            parsed_raw_order=items,
        ),
        pile_sort=PileSortRecord(
            prompt_verbatim="test",
            prompt_version="v1",
            response_verbatim="test",
            response_object_json={},
            input_tokens=80,
            output_tokens=40,
            latency_ms=2000,
            stop_reason="end_turn",
            parsed_piles=piles,
            parsed_matrix=matrix,
        ),
        interview=InterviewRecord(
            prompt_verbatim="test",
            prompt_version="v1",
            response_verbatim="test",
            response_object_json={},
            input_tokens=60,
            output_tokens=10,
            latency_ms=800,
            stop_reason="end_turn",
            parsed_pile_labels=[f"pile_{i}" for i in range(len(piles))],
        ),
        sha256_manifest={
            "freelist_prompt": "a", "freelist_response": "b",
            "pilesort_prompt": "c", "pilesort_response": "d",
            "interview_prompt": "e", "interview_response": "f",
            "request_params": "g", "informant_record_total": "h",
        },
        qa_passed=True,
    )


def _synthetic_records() -> list[InformantRecord]:
    """Two models, 3 runs each, different pile structures."""
    items = ["mother", "father", "sister", "brother"]

    records = []
    # Model A: groups by generation (parents vs siblings)
    for i in range(3):
        records.append(_make_record(
            "model-a", i, items,
            [["mother", "father"], ["sister", "brother"]],
        ))
    # Model B: groups by gender
    for i in range(3):
        records.append(_make_record(
            "model-b", i, items,
            [["mother", "sister"], ["father", "brother"]],
        ))
    return records


def test_group_by_model():
    records = _synthetic_records()
    groups = group_by_model(records)
    assert set(groups.keys()) == {"model-a", "model-b"}
    assert len(groups["model-a"]) == 3
    assert len(groups["model-b"]) == 3


def test_run_pipeline_produces_domain_result():
    records = _synthetic_records()
    result = run_pipeline(records, analysis_version="test", n_bootstrap=10)

    assert result.domain_slug == "family"
    assert result.analysis_version == "test"
    assert len(result.models) == 2
    assert "model-a" in result.mds_coordinates
    assert "model-b" in result.mds_coordinates
    assert "model-a" in result.mds_uncertainty
    assert "model-b" in result.mds_uncertainty
    assert len(result.similarity_matrix) == 2
    assert len(result.similarity_ci) == 2
    assert result.consensus_score > 0
    assert result.groundings == []
    assert result.generated_lede == ""


def test_run_pipeline_populates_sutrop_fields():
    """Sutrop CSI and salience-index agreement are populated per model.

    SME_REVIEW.md §2.1: Sutrop CSI is more robust to list-length variance
    than Smith's S; the Spearman ρ between the two rankings is the QA
    signal for list-length variance affecting salience structure.
    """
    records = _synthetic_records()
    result = run_pipeline(records, analysis_version="test", n_bootstrap=10)

    # Per-model CSI entries
    assert set(result.sutrop_csi.keys()) == {"model-a", "model-b"}
    for mid, csi_list in result.sutrop_csi.items():
        assert len(csi_list) > 0, f"{mid} has no Sutrop CSI entries"
        # Each entry is a SutropCSI pydantic model with the right fields
        top = csi_list[0]
        assert top.item
        assert top.csi > 0
        assert top.f_mentions > 0
        assert top.n_runs == 3  # 3 runs per model in _synthetic_records
        assert top.mean_position >= 1.0

    # Per-model Smith's S vs Sutrop CSI Spearman ρ
    assert set(result.salience_index_agreement.keys()) == {"model-a", "model-b"}
    for mid, rho in result.salience_index_agreement.items():
        assert -1.0 <= rho <= 1.0, f"{mid} rho out of range: {rho}"


def test_pipeline_single_model():
    """Single model should produce a valid but trivial DomainResult."""
    items = ["mother", "father", "sister", "brother"]
    records = [
        _make_record("model-a", i, items, [["mother", "father"], ["sister", "brother"]])
        for i in range(3)
    ]
    result = run_pipeline(records, analysis_version="test", n_bootstrap=10)

    assert len(result.models) == 1
    assert result.mds_coordinates["model-a"] == (0.0, 0.0)
    assert result.consensus_score == 1.0


def test_write_result(tmp_path: Path):
    records = _synthetic_records()
    result = run_pipeline(records, analysis_version="0.1", n_bootstrap=10)

    out_path = write_result(result, tmp_path)

    assert out_path.exists()
    assert out_path.name == "0.1.json"
    assert out_path.parent.name == "family"

    # Verify it's valid JSON and round-trips
    data = json.loads(out_path.read_text())
    assert data["domain_slug"] == "family"
    assert len(data["mds_coordinates"]) == 2


def test_load_records_from_jsonl(tmp_path: Path):
    records = _synthetic_records()
    jsonl = tmp_path / "informants.jsonl"
    with open(jsonl, "w") as f:
        for rec in records:
            f.write(rec.model_dump_json() + "\n")

    loaded = load_records(jsonl, "family")
    assert len(loaded) == 6

    # Filter by domain
    loaded_other = load_records(jsonl, "holidays")
    assert len(loaded_other) == 0
