"""Tests for salience elbow detection and cross-model consensus."""

from cdb_analyze.consensus import (
    compute_cross_model_consensus,
    find_salience_elbow,
)


def test_clear_elbow():
    """A curve with a sharp drop should find the elbow at the bend."""
    # 8 high-salience items, then a sharp drop to a low tail
    ranked = [(f"item{i}", 1.0 - i * 0.02) for i in range(8)]  # 1.0 → 0.86
    ranked += [(f"tail{i}", 0.15 - i * 0.005) for i in range(20)]  # 0.15 → 0.05
    elbow = find_salience_elbow(ranked, min_items=5, max_items=28)
    # Elbow should be near the transition point (index ~8)
    assert 7 <= elbow <= 12


def test_flat_curve_returns_max():
    """A flat curve (all items equally salient) should return max_items."""
    ranked = [(f"item{i}", 0.5) for i in range(30)]
    elbow = find_salience_elbow(ranked, min_items=5, max_items=30)
    assert elbow == 30


def test_short_list_returns_all():
    """A list shorter than min_items should return its full length."""
    ranked = [(f"item{i}", 1.0 - i * 0.1) for i in range(5)]
    elbow = find_salience_elbow(ranked, min_items=10)
    assert elbow == 5


def test_min_items_floor():
    """Elbow should never be below min_items even if the curve drops early."""
    # Immediate drop: one high item, then flat tail
    ranked = [("top", 1.0)] + [(f"tail{i}", 0.01) for i in range(30)]
    elbow = find_salience_elbow(ranked, min_items=10, max_items=31)
    assert elbow >= 10


def test_max_items_ceiling():
    """Elbow should never exceed max_items."""
    # Gradual decline — no clear elbow within the range
    ranked = [(f"item{i}", 1.0 - i * 0.01) for i in range(100)]
    elbow = find_salience_elbow(ranked, min_items=5, max_items=50)
    assert elbow <= 50


def test_realistic_smiths_s_curve():
    """Simulate a realistic Smith's S consensus curve from CDA free listing.

    High-salience core terms (mother, father, etc.) drop moderately,
    then the curve flattens through a long tail of rare items.
    """
    # Core items: steep but not vertical
    core = [(f"core{i}", 0.95 - i * 0.03) for i in range(15)]  # 0.95 → 0.53
    # Transition zone
    transition = [(f"mid{i}", 0.45 - i * 0.02) for i in range(5)]  # 0.45 → 0.37
    # Long tail
    tail = [(f"rare{i}", 0.30 - i * 0.003) for i in range(40)]  # 0.30 → 0.18

    ranked = core + transition + tail
    elbow = find_salience_elbow(ranked, min_items=10, max_items=60)
    # Should find the elbow somewhere in the core-to-transition zone
    assert 12 <= elbow <= 25


def test_empty_list():
    """Empty list returns 0."""
    assert find_salience_elbow([]) == 0


def test_single_item():
    """Single item returns 1."""
    assert find_salience_elbow([("only", 1.0)]) == 1


# ── Cross-model consensus tests ────────────────────────────────────

from datetime import date, datetime  # noqa: E402 — section-scoped imports for cross-model tests

from cdb_core import FreelistRecord, InformantRecord, InterviewRecord, PileSortRecord  # noqa: E402


def _make_record(
    model_id: str,
    raw_order: list[str],
    run_index: int = 0,
) -> InformantRecord:
    """Minimal InformantRecord with free list data for consensus tests."""
    n = len(raw_order)
    matrix = [[1] * n for _ in range(n)]
    return InformantRecord(
        informant_id=f"test_{model_id}_{run_index}",
        domain_slug="family",
        run_index=run_index,
        collection_date=datetime(2026, 4, 13),
        model_id=model_id,
        model_version_returned=model_id,
        family="test",
        provider="anthropic",
        provider_request_id="msg_test",
        knowledge_cutoff=date(2025, 5, 1),
        open_weights=False,
        origin_country="us",
        alignment_method=None,
        collection_method="anthropic_api",
        api_endpoint="https://test",
        api_version="2023-06-01",
        temperature=0.7,
        top_p=None,
        max_tokens=4096,
        system_prompt="",
        freelist=FreelistRecord(
            prompt_verbatim="test",
            prompt_version="v1",
            response_verbatim="test",
            response_object_json={},
            input_tokens=50,
            output_tokens=20,
            latency_ms=500,
            stop_reason="end_turn",
            parsed_items=raw_order,
            parsed_raw_order=raw_order,
        ),
        pile_sort=PileSortRecord(
            prompt_verbatim="test",
            prompt_version="v1",
            response_verbatim="test",
            response_object_json={},
            input_tokens=50,
            output_tokens=20,
            latency_ms=400,
            stop_reason="end_turn",
            parsed_piles=[raw_order],
            parsed_matrix=matrix,
        ),
        interview=InterviewRecord(
            prompt_verbatim="test",
            prompt_version="v1",
            response_verbatim="test",
            response_object_json={},
            input_tokens=30,
            output_tokens=10,
            latency_ms=200,
            stop_reason="end_turn",
            parsed_pile_labels=["label"],
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


def test_cross_model_consensus_pools_all_models():
    """Cross-model consensus should include items from all models."""
    records_by_model = {
        "model_a": [
            _make_record("model_a", ["mother", "father", "sister"]),
        ],
        "model_b": [
            _make_record("model_b", ["mother", "father", "cousin"]),
        ],
    }
    consensus = compute_cross_model_consensus(records_by_model)
    items = [item for item, _ in consensus]

    # "mother" and "father" appear in both → highest salience
    assert items[0] == "mother"
    assert items[1] == "father"
    # "sister" and "cousin" each appear in one model
    assert "sister" in items
    assert "cousin" in items


def test_cross_model_consensus_shared_items_rank_higher():
    """Items appearing across multiple models should outrank model-specific items."""
    records_by_model = {
        "model_a": [
            _make_record("model_a", ["mother", "father", "aunt", "uncle"]),
            _make_record("model_a", ["mother", "father", "aunt", "uncle"], run_index=1),
        ],
        "model_b": [
            _make_record("model_b", ["mother", "father", "cousin", "nephew"]),
            _make_record("model_b", ["mother", "father", "cousin", "nephew"], run_index=1),
        ],
    }
    consensus = compute_cross_model_consensus(records_by_model)
    salience = {item: s for item, s in consensus}

    # "mother" and "father" appear in all 4 runs → highest
    # "aunt" appears in 2 runs (model_a only), "cousin" in 2 runs (model_b only)
    assert salience["mother"] > salience["aunt"]
    assert salience["mother"] > salience["cousin"]
