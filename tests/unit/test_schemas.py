"""Unit tests for cdb_core schemas — construct minimal instances, verify JSON round-trip.

See PHASE_0_TASKS.md P0-T3 acceptance criteria.
"""

from datetime import date, datetime

from cdb_core.ids import run_id
from cdb_core.schemas import (
    BootstrapEllipse,
    CooccurrenceMatrix,
    Domain,
    DomainResult,
    FreeList,
    FreelistRecord,
    GroundingRef,
    InformantRecord,
    InterviewRecord,
    ModelRef,
    PileSort,
    PileSortRecord,
    RawResponse,
)

# ── Fixtures ──

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


def _bootstrap_ellipse() -> BootstrapEllipse:
    return BootstrapEllipse(
        center=(0.5, -0.3),
        semi_major=0.12,
        semi_minor=0.08,
        rotation_rad=0.45,
        n_bootstrap=1000,
    )


def _freelist_record() -> FreelistRecord:
    return FreelistRecord(
        prompt_verbatim="List every family term you can think of.",
        prompt_version="v1",
        response_verbatim="1. mother\n2. father\n3. sister",
        response_object_json={"id": "msg_123", "model": "claude-opus-4-6"},
        input_tokens=50,
        output_tokens=20,
        latency_ms=1200,
        stop_reason="end_turn",
        parsed_items=["mother", "father", "sister"],
        parsed_raw_order=["mother", "father", "sister"],
    )


def _pilesort_record() -> PileSortRecord:
    return PileSortRecord(
        prompt_verbatim="Sort these items into piles.",
        prompt_version="v1",
        response_verbatim="Pile 1: mother, father\nPile 2: sister",
        response_object_json={"id": "msg_456"},
        input_tokens=60,
        output_tokens=30,
        latency_ms=1500,
        stop_reason="end_turn",
        parsed_piles=[["mother", "father"], ["sister"]],
        parsed_matrix=[[1, 1, 0], [1, 1, 0], [0, 0, 1]],
    )


def _interview_record() -> InterviewRecord:
    return InterviewRecord(
        prompt_verbatim="Name each pile.",
        prompt_version="v1",
        response_verbatim="Pile 1: Parents\nPile 2: Siblings",
        response_object_json={"id": "msg_789"},
        input_tokens=40,
        output_tokens=15,
        latency_ms=800,
        stop_reason="end_turn",
        parsed_pile_labels=["Parents", "Siblings"],
    )


# ── Tests ──

def test_run_id_deterministic():
    id1 = run_id("claude-opus-4-6", "family", "free_list", "v1", 0)
    id2 = run_id("claude-opus-4-6", "family", "free_list", "v1", 0)
    assert id1 == id2
    assert len(id1) == 16


def test_run_id_varies_with_input():
    id1 = run_id("claude-opus-4-6", "family", "free_list", "v1", 0)
    id2 = run_id("claude-opus-4-6", "family", "free_list", "v1", 1)
    assert id1 != id2


def test_bootstrap_ellipse_round_trip():
    obj = _bootstrap_ellipse()
    json_str = obj.model_dump_json()
    restored = BootstrapEllipse.model_validate_json(json_str)
    assert restored == obj


def test_model_ref_round_trip():
    obj = _model_ref()
    json_str = obj.model_dump_json()
    restored = ModelRef.model_validate_json(json_str)
    assert restored == obj


def test_domain_round_trip():
    obj = Domain(
        slug="family",
        version="v1",
        display_name="Family Terms",
        prompt_seed="family terms and kinship words",
    )
    json_str = obj.model_dump_json()
    restored = Domain.model_validate_json(json_str)
    assert restored == obj
    assert restored.truncation_k == 25


def test_raw_response_round_trip():
    obj = RawResponse(
        run_id="abc123",
        model=_model_ref(),
        domain_slug="family",
        step="free_list",
        prompt_version="v1",
        run_index=0,
        timestamp=datetime(2026, 4, 1, 12, 0, 0),
        request={"prompt": "test"},
        response={"text": "result"},
        latency_ms=1000,
    )
    json_str = obj.model_dump_json()
    restored = RawResponse.model_validate_json(json_str)
    assert restored == obj


def test_free_list_round_trip():
    obj = FreeList(
        run_id="abc123",
        model=_model_ref(),
        domain_slug="family",
        items=["mother", "father"],
        raw_order=["mother", "father", "sister"],
    )
    json_str = obj.model_dump_json()
    restored = FreeList.model_validate_json(json_str)
    assert restored == obj


def test_pile_sort_round_trip():
    obj = PileSort(
        run_id="abc123",
        model=_model_ref(),
        domain_slug="family",
        items=["mother", "father", "sister"],
        piles=[["mother", "father"], ["sister"]],
        pile_labels=["Parents", "Siblings"],
    )
    json_str = obj.model_dump_json()
    restored = PileSort.model_validate_json(json_str)
    assert restored == obj


def test_cooccurrence_matrix_round_trip():
    obj = CooccurrenceMatrix(
        domain_slug="family",
        model=_model_ref(),
        items=["mother", "father"],
        matrix=[[1.0, 0.8], [0.8, 1.0]],
    )
    json_str = obj.model_dump_json()
    restored = CooccurrenceMatrix.model_validate_json(json_str)
    assert restored == obj


def test_grounding_ref_published_round_trip():
    obj = GroundingRef(
        baseline_id="romney_1996",
        baseline_kind="published",
        domain_slug="family",
        source_citation="Romney, A. K., et al. (1996).",
        source_url="https://doi.org/10.1234/example",
        collected_year=1990,
        n_human_informants=122,
        population_description="US college students, ages 18-22, n=122",
        method="pile sort (Romney protocol)",
        irb_status="not_applicable",
        mds_coordinate=(0.1, -0.2),
        distance_to_nearest_model=0.35,
        nearest_model_id="claude-opus-4-6",
        item_intersection_size=20,
        item_intersection_total=25,
    )
    json_str = obj.model_dump_json()
    restored = GroundingRef.model_validate_json(json_str)
    assert restored == obj
    assert restored.submitter_name is None
    assert restored.mds_uncertainty is None


def test_grounding_ref_researcher_round_trip():
    obj = GroundingRef(
        baseline_id="tanaka_2026_kyoto",
        baseline_kind="researcher",
        domain_slug="family",
        source_citation="Tanaka, Y. (2026). Kyoto kinship study.",
        source_url=None,
        collected_year=2025,
        n_human_informants=80,
        population_description="Japanese university students, Kyoto, n=80",
        method="free list + pile sort",
        irb_status="approved",
        submitter_name="Yuki Tanaka",
        submitter_institution="Kyoto University",
        submitter_contact="0000-0001-2345-6789",
        submission_date=date(2026, 4, 1),
        mds_coordinate=(0.3, 0.1),
        mds_uncertainty=_bootstrap_ellipse(),
        distance_to_nearest_model=0.28,
        nearest_model_id="gpt-4o",
        item_intersection_size=18,
        item_intersection_total=25,
    )
    json_str = obj.model_dump_json()
    restored = GroundingRef.model_validate_json(json_str)
    assert restored == obj
    assert restored.submitter_name == "Yuki Tanaka"


def test_domain_result_with_groundings_round_trip():
    grounding = GroundingRef(
        baseline_id="romney_1996",
        baseline_kind="published",
        domain_slug="family",
        source_citation="Romney et al. (1996)",
        source_url=None,
        collected_year=1990,
        n_human_informants=122,
        population_description="US college students",
        method="pile sort",
        irb_status="not_applicable",
        mds_coordinate=(0.0, 0.0),
        distance_to_nearest_model=0.5,
        nearest_model_id="claude-opus-4-6",
        item_intersection_size=25,
        item_intersection_total=25,
    )
    obj = DomainResult(
        domain_slug="family",
        analysis_version="0.1",
        models=[_model_ref()],
        free_lists={"claude-opus-4-6": FreeList(
            run_id="abc", model=_model_ref(), domain_slug="family",
            items=["mother"], raw_order=["mother"],
        )},
        mds_coordinates={"claude-opus-4-6": (0.5, -0.3)},
        mds_uncertainty={"claude-opus-4-6": _bootstrap_ellipse()},
        similarity_matrix=[[1.0]],
        similarity_ci=[[(0.95, 1.0)]],
        consensus_score=3.2,
        consensus_ci=(2.8, 3.6),
        groundings=[grounding],
        selected_baseline_id="romney_1996",
        generated_lede="Claude organizes family terms into two primary clusters.",
        generated_at=datetime(2026, 4, 1, 12, 0, 0),
    )
    json_str = obj.model_dump_json()
    restored = DomainResult.model_validate_json(json_str)
    assert restored == obj
    assert len(restored.groundings) == 1
    assert restored.selected_baseline_id == "romney_1996"


def test_domain_result_ungrounded():
    """Ungrounded is a normal first-class state — empty groundings list."""
    obj = DomainResult(
        domain_slug="holidays",
        analysis_version="0.1",
        models=[_model_ref()],
        free_lists={},
        mds_coordinates={},
        mds_uncertainty={},
        similarity_matrix=[],
        similarity_ci=[],
        consensus_score=2.5,
        consensus_ci=(2.0, 3.0),
        groundings=[],
        selected_baseline_id=None,
        generated_lede="Models cluster holiday terms by season and tradition.",
        generated_at=datetime(2026, 4, 1, 12, 0, 0),
    )
    json_str = obj.model_dump_json()
    restored = DomainResult.model_validate_json(json_str)
    assert restored.groundings == []
    assert restored.selected_baseline_id is None


def test_freelist_record_round_trip():
    obj = _freelist_record()
    json_str = obj.model_dump_json()
    restored = FreelistRecord.model_validate_json(json_str)
    assert restored == obj


def test_pilesort_record_round_trip():
    obj = _pilesort_record()
    json_str = obj.model_dump_json()
    restored = PileSortRecord.model_validate_json(json_str)
    assert restored == obj


def test_interview_record_round_trip():
    obj = _interview_record()
    json_str = obj.model_dump_json()
    restored = InterviewRecord.model_validate_json(json_str)
    assert restored == obj


def test_informant_record_round_trip():
    obj = InformantRecord(
        informant_id="a1b2c3d4e5f67890",
        domain_slug="family",
        run_index=0,
        collection_date=datetime(2026, 4, 1, 12, 0, 0),
        model_id="claude-opus-4-6",
        model_version_returned="claude-opus-4-6-20260301",
        family="claude",
        provider="anthropic",
        provider_request_id="req_abc123",
        knowledge_cutoff=date(2025, 8, 1),
        open_weights=False,
        origin_country="us",
        alignment_method="Constitutional AI",
        collection_method="anthropic_api",
        api_endpoint="https://api.anthropic.com/v1/messages",
        api_version="2023-06-01",
        temperature=0.7,
        top_p=None,
        max_tokens=4096,
        system_prompt="You are participating in a cognitive anthropology study.",
        freelist=_freelist_record(),
        pile_sort=_pilesort_record(),
        interview=_interview_record(),
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
    json_str = obj.model_dump_json()
    restored = InformantRecord.model_validate_json(json_str)
    assert restored == obj
    assert restored.model_version_returned == "claude-opus-4-6-20260301"
    assert len(restored.sha256_manifest) == 8


def test_informant_record_sha256_manifest_keys():
    """Verify the eight mandatory manifest keys per ARCHITECTURE.md §3.2."""
    expected_keys = {
        "freelist_prompt",
        "freelist_response",
        "pilesort_prompt",
        "pilesort_response",
        "interview_prompt",
        "interview_response",
        "request_params",
        "informant_record_total",
    }
    obj = InformantRecord(
        informant_id="test",
        domain_slug="family",
        run_index=0,
        collection_date=datetime(2026, 1, 1),
        model_id="test-model",
        model_version_returned="test-model-v1",
        family="test",
        provider="anthropic",
        provider_request_id="req_test",
        knowledge_cutoff=None,
        open_weights=False,
        origin_country="us",
        alignment_method=None,
        collection_method="anthropic_api",
        api_endpoint="https://api.anthropic.com/v1/messages",
        api_version="2023-06-01",
        temperature=0.7,
        top_p=None,
        max_tokens=4096,
        system_prompt="test",
        freelist=_freelist_record(),
        pile_sort=_pilesort_record(),
        interview=_interview_record(),
        sha256_manifest={k: "0" * 64 for k in expected_keys},
        qa_passed=True,
    )
    assert set(obj.sha256_manifest.keys()) == expected_keys


def test_pilesort_item_source_default():
    """PileSortRecord.item_source defaults to 'own_freelist'."""
    obj = _pilesort_record()
    assert obj.item_source == "own_freelist"


def test_pilesort_item_source_consensus():
    obj = PileSortRecord(
        prompt_verbatim="test",
        prompt_version="v1",
        response_verbatim="test",
        response_object_json={},
        input_tokens=10,
        output_tokens=10,
        latency_ms=100,
        stop_reason="end_turn",
        parsed_piles=[["a", "b"]],
        parsed_matrix=[[1, 1], [1, 1]],
        item_source="consensus:claude-opus-4-6",
    )
    assert obj.item_source == "consensus:claude-opus-4-6"
    json_str = obj.model_dump_json()
    restored = PileSortRecord.model_validate_json(json_str)
    assert restored.item_source == "consensus:claude-opus-4-6"


def test_informant_record_collection_mode_default():
    """InformantRecord.collection_mode defaults to 'single_pass'."""
    obj = InformantRecord(
        informant_id="test",
        domain_slug="family",
        run_index=0,
        collection_date=datetime(2026, 1, 1),
        model_id="test-model",
        model_version_returned="test-model-v1",
        family="test",
        provider="anthropic",
        provider_request_id="req_test",
        knowledge_cutoff=None,
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
        freelist=_freelist_record(),
        pile_sort=_pilesort_record(),
        interview=_interview_record(),
        sha256_manifest={k: "0" * 64 for k in [
            "freelist_prompt", "freelist_response",
            "pilesort_prompt", "pilesort_response",
            "interview_prompt", "interview_response",
            "request_params", "informant_record_total",
        ]},
        qa_passed=True,
    )
    assert obj.collection_mode == "single_pass"


def test_informant_record_collection_mode_two_pass():
    obj = InformantRecord(
        informant_id="test",
        domain_slug="family",
        run_index=0,
        collection_date=datetime(2026, 1, 1),
        model_id="test-model",
        model_version_returned="test-model-v1",
        family="test",
        provider="anthropic",
        provider_request_id="req_test",
        knowledge_cutoff=None,
        open_weights=False,
        origin_country="us",
        alignment_method=None,
        collection_method="anthropic_api",
        collection_mode="two_pass",
        api_endpoint="https://api.anthropic.com/v1/messages",
        api_version="2023-06-01",
        temperature=0.7,
        top_p=None,
        max_tokens=4096,
        system_prompt="",
        freelist=_freelist_record(),
        pile_sort=_pilesort_record(),
        interview=_interview_record(),
        sha256_manifest={k: "0" * 64 for k in [
            "freelist_prompt", "freelist_response",
            "pilesort_prompt", "pilesort_response",
            "interview_prompt", "interview_response",
            "request_params", "informant_record_total",
        ]},
        qa_passed=True,
    )
    assert obj.collection_mode == "two_pass"
    json_str = obj.model_dump_json()
    restored = InformantRecord.model_validate_json(json_str)
    assert restored.collection_mode == "two_pass"
