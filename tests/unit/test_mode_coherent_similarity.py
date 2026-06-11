"""Tests for FOOD-FIX-A: mode-coherent similarity basis in mixed-mode corpora.

Verifies that run_pipeline(similarity_collection_mode="single_pass") eliminates
the constant-row collapse that arises when single_pass and cross_model_consensus
records coexist in the same corpus.

Acceptance criteria addressed:
  A6 — mixed-mode fixture reproduces collapse without filter, not with filter.
  A7 — WARNING diagnostic names both model_ids and fires at level WARNING.
  A8 — single-mode fixture produces byte-identical outputs with/without param.

See: docs/status/2026-06-11-phase9b-food-campaign.md
     .claude/agent-memory/cda_sme/project_phase9b_food_guard_trip.md (round 2)
     .claude/agent-memory/cda_sme/project_food_fix_a_verdict.md (F8, F9)
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime

import pytest
from cdb_analyze.pipeline import run_pipeline
from cdb_core import FreelistRecord, InformantRecord, InterviewRecord, PileSortRecord

# ---------------------------------------------------------------------------
# Fixture builders
# ---------------------------------------------------------------------------


def _make_record(
    model_id: str,
    run_index: int,
    freelist_items: list[str],
    piles: list[list[str]],
    *,
    domain_slug: str = "food",
    collection_mode: str = "single_pass",
) -> InformantRecord:
    """Build a minimal InformantRecord with configurable collection_mode."""
    all_items = [item for pile in piles for item in pile]
    n = len(all_items)
    idx = {item: i for i, item in enumerate(all_items)}
    matrix = [[0] * n for _ in range(n)]
    for pile in piles:
        for a in pile:
            for b in pile:
                matrix[idx[a]][idx[b]] = 1

    return InformantRecord(
        informant_id=f"{model_id}_{run_index}",
        domain_slug=domain_slug,
        run_index=run_index,
        collection_date=datetime(2026, 6, 11, tzinfo=UTC),
        model_id=model_id,
        model_version_returned=f"{model_id}-v1",
        family="test",
        provider="anthropic",
        provider_request_id=f"req_{model_id}_{run_index}",
        knowledge_cutoff=None,
        open_weights=False,
        origin_country="us",
        alignment_method=None,
        collection_method="anthropic_api",
        collection_mode=collection_mode,
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
            parsed_items=freelist_items,
            parsed_raw_order=freelist_items,
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


def _make_single_pass_record(
    model_id: str,
    run_index: int,
    freelist_items: list[str],
    piles: list[list[str]],
    domain_slug: str = "food",
) -> InformantRecord:
    """Single-pass record with its own free-list items."""
    return _make_record(
        model_id, run_index, freelist_items, piles,
        domain_slug=domain_slug, collection_mode="single_pass",
    )


def _make_consensus_record(
    model_id: str,
    run_index: int,
    canonical_deck: list[str],
    piles: list[list[str]],
    domain_slug: str = "food",
) -> InformantRecord:
    """Cross-model consensus record.

    The free-list is empty (placeholder, as per the cross_model_consensus
    design). Items come from the pile-sort canonical card deck only.
    This is the item-source asymmetry that causes the collapse: the
    else-branch in cooccurrence.py L98-101 fires and populates mat.items
    from pile_sort.parsed_piles instead of freelist.parsed_items.
    """
    return _make_record(
        model_id, run_index, [],  # empty freelist = consensus mode placeholder
        piles,
        domain_slug=domain_slug, collection_mode="cross_model_consensus",
    )


# ---------------------------------------------------------------------------
# Minimal mixed-mode fixture that reproduces the FOOD-FIX-A collapse.
#
# Design (F9 binding requirement: fixture must exercise BOTH the constant-row
# mechanism AND the WARNING fire):
#
#   - model-sp-a: single_pass only, free-list has BOTH sp-a unique items AND
#     a shared core. Pile structure VARIES across runs so real variance exists
#     when the item set is large enough. The collapse mechanism fires ONLY when
#     the shared-items intersection collapses to the small CONSENSUS_DECK core.
#   - model-sp-b: single_pass only, free-list has BOTH sp-b unique items AND
#     the same shared core. Pile structure varies across runs.
#   - model-cm-c: cross_model_consensus only, empty freelist, piles over
#     CONSENSUS_DECK only. This forces the 3-way intersection to collapse to
#     CONSENSUS_DECK items that appear in all three models' item sets. On that
#     small intersection, model-sp-a's pile structure IS constant (it always
#     puts the CONSENSUS_DECK items in the same pile), producing a constant
#     upper-triangle vector -> zero variance -> NaN -> WARNING -> 0.5 null.
#
# After mode filter (single_pass only):
#   - model-cm-c is dropped. The 2-model intersection expands to SHARED_CORE
#     + items both sp-a and sp-b happen to share. With the larger intersection
#     and varying pile structures, the NaN path is not triggered.
# ---------------------------------------------------------------------------

# Items that all three single_pass models free-list (3-model shared core).
SP_SHARED = ["bread", "rice", "pasta", "noodles", "beans"]
# sp-a exclusive items
SP_A_ONLY = ["naan", "tortilla"]
# sp-b exclusive items
SP_B_ONLY = ["sushi", "ramen"]
# sp-c exclusive items
SP_C_ONLY = ["taco", "dumpling"]
# Consensus deck = small subset that model-cm-d pile-sorts.
# MUST be a subset of SP_SHARED so it appears in the 4-way intersection.
CONSENSUS_DECK = ["bread", "rice", "pasta"]


def _make_mixed_mode_corpus() -> list[InformantRecord]:
    """Four models: 3 single_pass + 1 cross_model_consensus.

    model-sp-a: 3 single_pass runs with free-list = SP_SHARED + SP_A_ONLY.
        On the small CONSENSUS_DECK subset, every run puts all three items
        in the same pile -> constant sub-vector on the 4-way intersection
        -> NaN rescue -> WARNING -> 0.5 null for (sp-a, X) pairs.
    model-sp-b: 3 single_pass runs with free-list = SP_SHARED + SP_B_ONLY.
        Pile structure varies across runs (different from sp-a).
    model-sp-c: 3 single_pass runs with free-list = SP_SHARED + SP_C_ONLY.
        Pile structure varies across runs (different from sp-a and sp-b).
    model-cm-d: 2 cross_model_consensus runs, empty freelist, piles over
        CONSENSUS_DECK only. Forces the 4-way intersection to CONSENSUS_DECK.
        On that 3-item intersection, sp-a is constant -> NaN.

    After mode filter (single_pass only):
        model-cm-d dropped. 3-model intersection = SP_SHARED (5 items).
        sp-a, sp-b, sp-c all have varying pile structures on SP_SHARED ->
        real variance -> no NaN rescue -> no constant row.
    """
    records: list[InformantRecord] = []

    sp_a_items = SP_SHARED + SP_A_ONLY

    # model-sp-a pile structures:
    # - CONSENSUS_DECK items (bread, rice, pasta) ALWAYS in ONE pile together.
    # - The remaining items vary across runs.
    # On the 4-way intersection (CONSENSUS_DECK = 3 items), sp-a is constant:
    # every run co-sorts bread+rice+pasta. Upper-tri has only 1 value (=1.0) ->
    # zero variance -> corrcoef NaN.
    # On the 3-way intersection (SP_SHARED = 5 items), noodles and beans vary
    # across runs -> real variance -> no NaN.
    sp_a_piles_by_run = [
        [["bread", "rice", "pasta"], ["noodles"], ["beans", "naan"], ["tortilla"]],
        [["bread", "rice", "pasta"], ["noodles", "beans"], ["naan"], ["tortilla"]],
        [["bread", "rice", "pasta"], ["noodles", "tortilla"], ["beans"], ["naan"]],
    ]
    for i, piles in enumerate(sp_a_piles_by_run):
        records.append(_make_single_pass_record(
            "model-sp-a", i, sp_a_items, piles,
        ))

    # model-sp-b: varying pile structures on SP_SHARED + SP_B_ONLY.
    sp_b_items = SP_SHARED + SP_B_ONLY
    sp_b_piles_by_run = [
        [["bread", "noodles"], ["rice", "pasta", "beans"], ["sushi"], ["ramen"]],
        [["bread", "rice"], ["pasta", "beans", "noodles"], ["sushi", "ramen"]],
        [["bread", "pasta", "beans"], ["rice", "noodles"], ["sushi"], ["ramen"]],
    ]
    for i, piles in enumerate(sp_b_piles_by_run):
        records.append(_make_single_pass_record(
            "model-sp-b", i, sp_b_items, piles,
        ))

    # model-sp-c: varying pile structures on SP_SHARED + SP_C_ONLY.
    sp_c_items = SP_SHARED + SP_C_ONLY
    sp_c_piles_by_run = [
        [["rice", "beans", "noodles"], ["bread", "pasta"], ["taco"], ["dumpling"]],
        [["rice", "pasta"], ["bread", "beans", "noodles"], ["taco", "dumpling"]],
        [["rice", "noodles"], ["bread", "pasta", "beans"], ["taco"], ["dumpling"]],
    ]
    for i, piles in enumerate(sp_c_piles_by_run):
        records.append(_make_single_pass_record(
            "model-sp-c", i, sp_c_items, piles,
        ))

    # model-cm-d: cross_model_consensus, empty freelist, piles over CONSENSUS_DECK.
    # mat.items = CONSENSUS_DECK = {bread, rice, pasta} (3 items).
    # 4-way intersection collapses to CONSENSUS_DECK.
    # sp-a always co-sorts all 3 CONSENSUS_DECK items in one pile -> constant.
    cm_d_piles_by_run = [
        [["bread", "rice"], ["pasta"]],
        [["bread", "pasta"], ["rice"]],
    ]
    for i, piles in enumerate(cm_d_piles_by_run):
        records.append(_make_consensus_record(
            "model-cm-d", i, CONSENSUS_DECK, piles,
        ))

    return records


def _make_single_mode_corpus() -> list[InformantRecord]:
    """Three single_pass-only models — baseline for byte-identity test (A8).

    All records have collection_mode="single_pass". Running
    run_pipeline() with similarity_collection_mode=None and with
    similarity_collection_mode="single_pass" must produce byte-identical
    results for all protected fields.
    """
    records: list[InformantRecord] = []
    items_a = ["mother", "father", "sister", "brother"]
    items_b = ["mother", "father", "sister", "brother"]
    items_c = ["mother", "father", "sister", "brother"]

    for i in range(3):
        records.append(_make_single_pass_record(
            "model-a", i, items_a,
            [["mother", "father"], ["sister", "brother"]],
            domain_slug="family",
        ))
        records.append(_make_single_pass_record(
            "model-b", i, items_b,
            [["mother", "sister"], ["father", "brother"]],
            domain_slug="family",
        ))
        records.append(_make_single_pass_record(
            "model-c", i, items_c,
            [["mother", "brother"], ["father", "sister"]],
            domain_slug="family",
        ))

    return records


# ---------------------------------------------------------------------------
# Helper to detect a constant similarity row (the collapse fingerprint).
# ---------------------------------------------------------------------------

def _has_constant_similarity_row(similarity_matrix: list[list]) -> bool:
    """Return True if any non-diagonal row is constant across off-diagonal cells."""
    n = len(similarity_matrix)
    for i in range(n):
        row = similarity_matrix[i]
        off_diag = [row[j] for j in range(n) if j != i]
        if off_diag and len(set(off_diag)) == 1:
            return True
    return False


# ---------------------------------------------------------------------------
# Test 1: mixed-mode WITHOUT filter collapses (sanity: the bug exists).
# ---------------------------------------------------------------------------

def test_mixed_mode_without_filter_collapses() -> None:
    """Without the filter, the mixed-mode corpus produces at least one constant
    similarity row (the FOOD-FIX-A collapse mechanism).

    F9 binding: the fixture must exercise BOTH the constant-row mechanism AND
    the WARNING fire.
    """
    records = _make_mixed_mode_corpus()

    # Run WITHOUT mode filter — should reproduce the collapse.
    result_unfiltered = run_pipeline(
        records, analysis_version="test", n_bootstrap=5,
        similarity_collection_mode=None,
    )

    sim = result_unfiltered.similarity_matrix
    assert _has_constant_similarity_row(sim), (
        "Expected at least one constant similarity row in the unfiltered run "
        "(the FOOD-FIX-A collapse was not reproduced — check fixture design)."
    )


# ---------------------------------------------------------------------------
# Test 2: mixed-mode WITH filter eliminates the collapse.
# ---------------------------------------------------------------------------

def test_mixed_mode_with_filter_no_collapse() -> None:
    """With similarity_collection_mode='single_pass', the mixed-mode corpus
    produces no constant similarity rows and no bit-identical centrality artifact.
    """
    records = _make_mixed_mode_corpus()

    result_filtered = run_pipeline(
        records, analysis_version="test", n_bootstrap=5,
        similarity_collection_mode="single_pass",
    )

    sim = result_filtered.similarity_matrix
    assert not _has_constant_similarity_row(sim), (
        "After mode-coherent filtering, no constant similarity row should remain."
    )

    # Centrality scores: model-cm-d (zero single_pass records) must be absent
    # from the similarity slate; sp-a, sp-b, sp-c must all be present.
    centrality = result_filtered.cultural_centrality_scores
    model_ids_in_sim = list(centrality.keys())
    assert "model-cm-d" not in model_ids_in_sim, (
        "model-cm-d (zero single_pass records) must be absent from similarity slate."
    )
    assert "model-sp-a" in model_ids_in_sim
    assert "model-sp-b" in model_ids_in_sim
    assert "model-sp-c" in model_ids_in_sim

    # With 3 single_pass models, all centrality scores must differ from each other
    # (no bit-identical centrality artifact).
    score_a = centrality["model-sp-a"]
    score_b = centrality["model-sp-b"]
    score_c = centrality["model-sp-c"]
    assert not (score_a == score_b == score_c), (
        f"All three centrality scores are identical ({score_a}) — "
        "bit-identical centrality artifact was not eliminated."
    )


# ---------------------------------------------------------------------------
# Test 3: WARNING diagnostic fires, names both model_ids, is at WARNING level.
# ---------------------------------------------------------------------------

def test_nan_rescue_emits_warning(caplog: pytest.LogCaptureFixture) -> None:
    """The NaN rescue in compute_cross_model_similarity emits a WARNING that
    names both model_ids involved. F4 and F9 binding.
    """
    records = _make_mixed_mode_corpus()

    # Run without filter to trigger the NaN rescue path.
    with caplog.at_level(logging.WARNING, logger="cdb_analyze.mds"):
        run_pipeline(
            records, analysis_version="test", n_bootstrap=5,
            similarity_collection_mode=None,
        )

    # Find WARNING records from cdb_analyze.mds.
    warning_records = [
        r for r in caplog.records
        if r.levelno == logging.WARNING and r.name == "cdb_analyze.mds"
    ]

    assert len(warning_records) >= 1, (
        "Expected at least one WARNING from cdb_analyze.mds when NaN rescue fires. "
        "Check that the fixture exercises the constant-vector path."
    )

    # The WARNING must mention both involved model_ids (at least one pair).
    # The exact model involved is model-sp-a (constant upper-triangle vector
    # on the SHARED_CORE intersection due to identical pile structure across runs).
    warning_text = " ".join(r.getMessage() for r in warning_records)
    assert "model-sp-a" in warning_text, (
        f"Expected 'model-sp-a' in WARNING text. Got: {warning_text!r}"
    )
    # The WARNING must also contain "SHOULD NOT be read as a finding" (F4 binding).
    assert "SHOULD NOT be read as a finding" in warning_text, (
        f"WARNING must contain 'SHOULD NOT be read as a finding' (F4). Got: {warning_text!r}"
    )


# ---------------------------------------------------------------------------
# Test 4: single-mode corpus is byte-identical with/without parameter (A8).
# ---------------------------------------------------------------------------

def test_single_mode_byte_identical() -> None:
    """For a single_pass-only corpus, run_pipeline() with and without
    similarity_collection_mode='single_pass' must produce byte-identical
    values for similarity_matrix, cultural_centrality_scores, romney_eigenratio,
    consensus_type, consensus_score, centrality_ci, and mds_coordinates.

    This is the regression guard protecting family and holidays (F8 binding).
    """
    records = _make_single_mode_corpus()

    result_no_filter = run_pipeline(
        records, analysis_version="test", n_bootstrap=10,
        similarity_collection_mode=None,
    )
    result_with_filter = run_pipeline(
        records, analysis_version="test", n_bootstrap=10,
        similarity_collection_mode="single_pass",
    )

    # similarity_matrix: full numeric content
    sm_no = result_no_filter.similarity_matrix
    sm_with = result_with_filter.similarity_matrix
    assert len(sm_no) == len(sm_with), "similarity_matrix size differs"
    for i in range(len(sm_no)):
        for j in range(len(sm_no[i])):
            assert sm_no[i][j] == sm_with[i][j], (
                f"similarity_matrix[{i}][{j}] differs: {sm_no[i][j]} vs {sm_with[i][j]}"
            )

    # cultural_centrality_scores: full dict, float64 precision
    cs_no = result_no_filter.cultural_centrality_scores
    cs_with = result_with_filter.cultural_centrality_scores
    assert set(cs_no.keys()) == set(cs_with.keys()), "centrality score model sets differ"
    for mid in cs_no:
        assert cs_no[mid] == cs_with[mid], (
            f"cultural_centrality_scores[{mid!r}] differs: {cs_no[mid]} vs {cs_with[mid]}"
        )

    # romney_eigenratio
    assert result_no_filter.romney_eigenratio == result_with_filter.romney_eigenratio, (
        f"romney_eigenratio differs: "
        f"{result_no_filter.romney_eigenratio} vs {result_with_filter.romney_eigenratio}"
    )

    # consensus_type
    assert result_no_filter.consensus_type == result_with_filter.consensus_type, (
        f"consensus_type differs: "
        f"{result_no_filter.consensus_type} vs {result_with_filter.consensus_type}"
    )

    # consensus_score
    assert result_no_filter.consensus_score == result_with_filter.consensus_score, (
        f"consensus_score differs: "
        f"{result_no_filter.consensus_score} vs {result_with_filter.consensus_score}"
    )

    # centrality_ci: protected by F8 (Remedy B contract)
    cci_no = result_no_filter.centrality_ci
    cci_with = result_with_filter.centrality_ci
    assert set(cci_no.keys()) == set(cci_with.keys()), "centrality_ci model sets differ"
    for mid in cci_no:
        lo_no, hi_no = cci_no[mid]
        lo_with, hi_with = cci_with[mid]
        assert lo_no == lo_with and hi_no == hi_with, (
            f"centrality_ci[{mid!r}] differs: ({lo_no}, {hi_no}) vs ({lo_with}, {hi_with})"
        )

    # mds_coordinates: F8 binding (bootstrap path downstream of similarity_matrix)
    mc_no = result_no_filter.mds_coordinates
    mc_with = result_with_filter.mds_coordinates
    assert set(mc_no.keys()) == set(mc_with.keys()), "mds_coordinates model sets differ"
    for mid in mc_no:
        x_no, y_no = mc_no[mid]
        x_with, y_with = mc_with[mid]
        assert x_no == x_with and y_no == y_with, (
            f"mds_coordinates[{mid!r}] differs: ({x_no}, {y_no}) vs ({x_with}, {y_with})"
        )
