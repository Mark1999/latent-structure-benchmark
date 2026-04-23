"""Tests for compute_romney_eigenratio and its pipeline wiring.

Covers the nine tests required by F2-T02 (docs/status/2026-04-20-f2-t02-architect-plan.md §6).
All fixtures are synthetic — no real API calls (CLAUDE.md §6 rule 10).
No cdb_analyze LLM imports (CLAUDE.md §6 rule 12).
"""

from __future__ import annotations

from datetime import UTC, datetime

import numpy as np
from cdb_analyze.consensus import compute_romney_eigenratio
from cdb_core import (
    FreelistRecord,
    InformantRecord,
    InterviewRecord,
    PileSortRecord,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_record(
    model_id: str,
    run_index: int,
    items: list[str],
    piles: list[list[str]],
) -> InformantRecord:
    """Build a minimal InformantRecord for pipeline tests."""
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
        collection_date=datetime(2026, 4, 21, tzinfo=UTC),
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
            "freelist_prompt": "a" * 64,
            "freelist_response": "b" * 64,
            "pilesort_prompt": "c" * 64,
            "pilesort_response": "d" * 64,
            "interview_prompt": "e" * 64,
            "interview_response": "f" * 64,
            "request_params": "g" * 64,
            "informant_record_total": "h" * 64,
        },
        qa_passed=True,
    )


def _records_for_n_models(n: int) -> list[InformantRecord]:
    """Produce 3 runs × n models, all with the same pile structure."""
    items = ["mother", "father", "sister", "brother"]
    records = []
    for m in range(n):
        model_id = f"model-{m}"
        for run in range(3):
            records.append(_make_record(
                model_id, run, items,
                [["mother", "father"], ["sister", "brother"]],
            ))
    return records


# ---------------------------------------------------------------------------
# Test 1 — basic known-eigenvalue matrix
# ---------------------------------------------------------------------------

def test_compute_romney_eigenratio_basic():
    """4×4 matrix with known eigenvalues: ratio should match 1e-9 tolerance.

    Construct a circulant-like symmetric matrix whose eigenvalues are
    analytically derivable.  We use a rank-1 perturbation so λ₂ != 0:
    M = a * ones_matrix + b * I, eigenvalues: a*n+b (×1) and b (×(n-1)).
    With a=1, b=0.1, n=4: λ₁=4.1, λ₂=λ₃=λ₄=0.1. ratio = 41.0.
    """
    n = 4
    a, b = 1.0, 0.1
    # M[i][j] = a if i!=j, M[i][i] = a + b
    M = np.full((n, n), a, dtype=np.float64)
    np.fill_diagonal(M, a + b)

    # Eigenvalues of this matrix: λ₁ = a*(n-1) + (a+b) = a*n + b = 4.1
    #                              λ₂ = b = 0.1 (degenerate, multiplicity n-1)
    expected_ratio = (a * n + b) / b  # 41.0

    result = compute_romney_eigenratio(M)
    assert result is not None, "Expected a float ratio, got None"
    assert abs(result - expected_ratio) < 1e-9, (
        f"Expected ratio {expected_ratio}, got {result}"
    )


# ---------------------------------------------------------------------------
# Test 2 — n < 2 degenerate guard
# ---------------------------------------------------------------------------

def test_compute_romney_eigenratio_returns_none_for_n_less_than_2():
    """1×1 matrix (n=1) must return None without raising."""
    M = np.array([[1.0]], dtype=np.float64)
    result = compute_romney_eigenratio(M)
    assert result is None, f"Expected None for 1×1 matrix, got {result}"


# ---------------------------------------------------------------------------
# Test 3 — rank-1 (second eigenvalue ≈ 0) degenerate guard
# ---------------------------------------------------------------------------

def test_compute_romney_eigenratio_returns_none_when_second_eigenvalue_near_zero():
    """Rank-1 matrix (all ones): λ₂=0 — must return None rather than ±inf.

    The all-ones 4×4 matrix has eigenvalues [4, 0, 0, 0].
    λ₂ = 0 < 1e-12, so the function must return None.
    """
    M = np.ones((4, 4), dtype=np.float64)
    result = compute_romney_eigenratio(M)
    assert result is None, (
        f"Expected None for rank-1 all-ones matrix, got {result}"
    )


# ---------------------------------------------------------------------------
# Test 4 — 4-model shakedown fixture: eigenratio is not None
# ---------------------------------------------------------------------------

def test_romney_eigenratio_populated_for_n4_shakedown_fixture():
    """4-model fixture: romney_eigenratio is not None after pipeline run.

    Addresses shakedown Finding 2 (romney_eigenratio=None on all DomainResults).
    With 4 models whose pile structures differ (non-rank-1 similarity matrix),
    eigenratio must be computed and non-None.
    """
    from cdb_analyze.pipeline import run_pipeline

    items = ["mother", "father", "sister", "brother"]
    records = []
    # 4 models with slightly different pile structures to ensure non-rank-1 sim matrix
    pile_structures = [
        [["mother", "father"], ["sister", "brother"]],
        [["mother", "sister"], ["father", "brother"]],
        [["mother", "father"], ["sister", "brother"]],
        [["mother", "sister"], ["father", "brother"]],
    ]
    for m, piles in enumerate(pile_structures):
        for run in range(3):
            records.append(_make_record(f"model-{m}", run, items, piles))

    result = run_pipeline(records, analysis_version="test", n_bootstrap=5)
    assert result.romney_eigenratio is not None, (
        "romney_eigenratio should not be None for a 4-model fixture with "
        "non-rank-1 similarity structure"
    )


# ---------------------------------------------------------------------------
# Test 5 — small-n warning True when n_models < 15
# ---------------------------------------------------------------------------

def test_romney_small_n_warning_true_when_n_less_than_15():
    """n=4 models: romney_small_n_warning must be True (SME binding threshold n<15)."""
    from cdb_analyze.pipeline import run_pipeline

    items = ["mother", "father", "sister", "brother"]
    pile_structures = [
        [["mother", "father"], ["sister", "brother"]],
        [["mother", "sister"], ["father", "brother"]],
        [["mother", "father"], ["sister", "brother"]],
        [["mother", "sister"], ["father", "brother"]],
    ]
    records = []
    for m, piles in enumerate(pile_structures):
        for run in range(3):
            records.append(_make_record(f"model-{m}", run, items, piles))

    result = run_pipeline(records, analysis_version="test", n_bootstrap=5)

    # n=4 < 15 → small_n_warning must be True when eigenratio was computed
    if result.romney_eigenratio is not None:
        assert result.romney_small_n_warning is True, (
            "romney_small_n_warning should be True for n=4 (< 15 threshold)"
        )


# ---------------------------------------------------------------------------
# Test 5b — regression guard for the 2026-04-23 threshold reconciliation:
# n=8 now triggers True (previously False under the superseded n<8 rule)
# ---------------------------------------------------------------------------

def test_romney_small_n_warning_true_at_n_equals_8():
    """n=8 models: flag must be True under the n<15 rule.

    Regression guard against reverting to the pre-2026-04-23 n<8 threshold.
    Under the old rule, 8 >= 8 meant flag=False; under the current rule,
    8 < 15 means flag=True. See docs/status/2026-04-23-small-n-threshold-
    sme-amendment.md.
    """
    from cdb_analyze.pipeline import run_pipeline

    items = ["mother", "father", "sister", "brother"]
    records = []
    # Alternate pile structures across 8 models to guarantee non-rank-1 matrix
    for m in range(8):
        if m % 2 == 0:
            piles = [["mother", "father"], ["sister", "brother"]]
        else:
            piles = [["mother", "sister"], ["father", "brother"]]
        for run in range(3):
            records.append(_make_record(f"model-{m}", run, items, piles))

    result = run_pipeline(records, analysis_version="test", n_bootstrap=5)

    # n=8 < 15 → small_n_warning must be True
    assert result.romney_small_n_warning is True, (
        f"romney_small_n_warning should be True for n=8 under n<15 threshold; "
        f"got {result.romney_small_n_warning}"
    )


# ---------------------------------------------------------------------------
# Test 6 — small-n warning False when n_models >= 15
# ---------------------------------------------------------------------------

def test_romney_small_n_warning_false_when_n_geq_15():
    """Synthetic 15-model fixture: romney_small_n_warning must be False."""
    from cdb_analyze.pipeline import run_pipeline

    items = ["mother", "father", "sister", "brother"]
    records = []
    # Alternate pile structures across 15 models to guarantee non-rank-1 matrix
    for m in range(15):
        if m % 2 == 0:
            piles = [["mother", "father"], ["sister", "brother"]]
        else:
            piles = [["mother", "sister"], ["father", "brother"]]
        for run in range(3):
            records.append(_make_record(f"model-{m}", run, items, piles))

    result = run_pipeline(records, analysis_version="test", n_bootstrap=5)

    # n=15 >= 15 → small_n_warning must be False regardless of eigenratio
    assert result.romney_small_n_warning is False, (
        f"romney_small_n_warning should be False for n=15; got {result.romney_small_n_warning}"
    )


# ---------------------------------------------------------------------------
# Test 7 — romney_consensus_pass True when eigenratio >= 5.0
# ---------------------------------------------------------------------------

def test_romney_consensus_pass_threshold_5():
    """Engineered similarity matrix with eigenratio >= 5.0: pass=True, warning=False."""
    from cdb_core import ROMNEY_THRESHOLD_LSB

    # Matrix with eigenvalues [10.1, 0.1, 0.1, 0.1] → ratio = 101.0 >= 5.0
    n = 4
    a, b = 2.5, 0.1   # λ₁ = a*n+b = 10.1, λ₂ = b = 0.1, ratio = 101.0
    M = np.full((n, n), a, dtype=np.float64)
    np.fill_diagonal(M, a + b)

    ratio = compute_romney_eigenratio(M)
    assert ratio is not None
    assert ratio >= ROMNEY_THRESHOLD_LSB, f"Expected ratio >= 5.0, got {ratio}"

    # Verify pass/warning semantics
    consensus_pass = ratio >= ROMNEY_THRESHOLD_LSB
    consensus_warning = 3.0 <= ratio < ROMNEY_THRESHOLD_LSB
    assert consensus_pass is True
    assert consensus_warning is False


# ---------------------------------------------------------------------------
# Test 8 — romney_consensus_warning True when eigenratio in [3.0, 5.0)
# ---------------------------------------------------------------------------

def test_romney_consensus_warning_zone_3_to_5():
    """Engineered similarity matrix with eigenratio in [3.0, 5.0): pass=False, warning=True."""
    from cdb_core import ROMNEY_THRESHOLD_CLASSIC, ROMNEY_THRESHOLD_LSB

    # We want λ₁/λ₂ ≈ 4.0 (in warning zone).
    # Use M = a*ones + b*I: ratio = (a*n+b)/b.
    # For n=4, want ratio=4: (4a+b)/b = 4 → 4a = 3b → a = 0.75*b.
    # With b=1.0, a=0.75: λ₁=4.0, λ₂=1.0, ratio=4.0.
    n = 4
    a, b = 0.75, 1.0
    M = np.full((n, n), a, dtype=np.float64)
    np.fill_diagonal(M, a + b)

    ratio = compute_romney_eigenratio(M)
    assert ratio is not None
    assert ROMNEY_THRESHOLD_CLASSIC <= ratio < ROMNEY_THRESHOLD_LSB, (
        f"Expected ratio in [3.0, 5.0), got {ratio}"
    )

    consensus_pass = ratio >= ROMNEY_THRESHOLD_LSB
    consensus_warning = ROMNEY_THRESHOLD_CLASSIC <= ratio < ROMNEY_THRESHOLD_LSB
    assert consensus_pass is False
    assert consensus_warning is True


# ---------------------------------------------------------------------------
# Test 9 — single-model degenerate: all four Romney fields clean, no exception
# ---------------------------------------------------------------------------

def test_romney_single_model_degenerate_no_exception():
    """n=1 model: all four Romney fields are None/False, no exception raised.

    The n<2 code path in pipeline.py must set:
      romney_eigenratio = None
      romney_consensus_pass = None
      romney_consensus_warning = None
      romney_small_n_warning = False
    """
    from cdb_analyze.pipeline import run_pipeline

    items = ["mother", "father", "sister", "brother"]
    records = [
        _make_record("model-a", i, items, [["mother", "father"], ["sister", "brother"]])
        for i in range(3)
    ]

    # Must not raise
    result = run_pipeline(records, analysis_version="test", n_bootstrap=5)

    assert len(result.models) == 1
    assert result.romney_eigenratio is None, (
        f"Expected None for single-model; got {result.romney_eigenratio}"
    )
    assert result.romney_consensus_pass is None, (
        f"Expected None for single-model; got {result.romney_consensus_pass}"
    )
    assert result.romney_consensus_warning is None, (
        f"Expected None for single-model; got {result.romney_consensus_warning}"
    )
    assert result.romney_small_n_warning is False, (
        f"Expected False for single-model; got {result.romney_small_n_warning}"
    )
