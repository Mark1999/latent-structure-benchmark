"""Tests for cdb_publish.derived — pure helper functions.

No real API calls. All tests use synthetic data.
See CLAUDE.md §6 R9 (no real API in tests).

Test plan (9 tests):
  1. r1_state_for — typical_concentration (deterministic=False, oci=10.0)
  2. r1_state_for — low_concentration (deterministic=False, oci=2.0)
  3. r1_state_for — deterministic (deterministic=True, oci=anything)
  4. r1_state_for — boundary: oci exactly at 3.0 → typical_concentration
     (oci < threshold is False at equality, so typical)
  5. top_freelist_terms — basic ranking by csi descending
  6. top_freelist_terms — k parameter respected (k=3 returns 3 entries)
  7. top_freelist_terms — stable tie-break lexicographic ascending
  8. top_freelist_terms — empty input returns empty list
  9. TOP_TERMS_METRIC constant value == "sutrop_csi"

See docs/status/2026-05-09-phase5-architect-plan.md §4 T3.
Per CDA SME plan-level verdict Q4: Sutrop CSI is the canonical
salience-rank metric; TOP_TERMS_METRIC names the choice for auditability.
"""

from __future__ import annotations

from cdb_core.schemas import SutropCSI, WithinModelResult
from cdb_publish.derived import DEFAULT_TOP_K, TOP_TERMS_METRIC, r1_state_for, top_freelist_terms
from cdb_publish.lede import OCI_LOW_CONCENTRATION_THRESHOLD

# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

def _make_wmr(
    model_id: str = "test-model",
    oci: float = 10.0,
    deterministic_output: bool = False,
) -> WithinModelResult:
    """Build a minimal WithinModelResult for testing."""
    return WithinModelResult(
        model_id=model_id,
        n_runs=5,
        oci=oci,
        deterministic_output=deterministic_output,
    )


def _make_csi(item: str, csi: float, f_mentions: int = 3, n_runs: int = 5) -> SutropCSI:
    """Build a SutropCSI entry for testing."""
    # mean_position derived from: CSI = F / (N × mP) => mP = F / (N × CSI)
    # Guard against division by zero for the test helper.
    mean_position = f_mentions / (n_runs * csi) if csi > 0 else 1.0
    return SutropCSI(
        item=item,
        csi=csi,
        f_mentions=f_mentions,
        n_runs=n_runs,
        mean_position=mean_position,
    )


# ---------------------------------------------------------------------------
# Test 1 — typical_concentration: deterministic=False, oci above threshold
# ---------------------------------------------------------------------------

def test_r1_state_typical_concentration() -> None:
    """r1_state_for returns 'typical_concentration' when oci is above threshold."""
    wmr = _make_wmr(oci=10.0, deterministic_output=False)
    assert r1_state_for(wmr) == "typical_concentration"


# ---------------------------------------------------------------------------
# Test 2 — low_concentration: deterministic=False, oci below threshold
# ---------------------------------------------------------------------------

def test_r1_state_low_concentration() -> None:
    """r1_state_for returns 'low_concentration' when oci is below threshold."""
    wmr = _make_wmr(oci=2.0, deterministic_output=False)
    assert r1_state_for(wmr) == "low_concentration"


# ---------------------------------------------------------------------------
# Test 3 — deterministic: deterministic_output=True, oci can be anything
# ---------------------------------------------------------------------------

def test_r1_state_deterministic_overrides_oci() -> None:
    """r1_state_for returns 'deterministic' when deterministic_output=True.

    The deterministic check takes priority regardless of the oci value.
    A model with deterministic_output=True AND oci=0.0 is still R1-c.
    """
    wmr_high_oci = _make_wmr(oci=10.0, deterministic_output=True)
    assert r1_state_for(wmr_high_oci) == "deterministic"

    wmr_zero_oci = _make_wmr(oci=0.0, deterministic_output=True)
    assert r1_state_for(wmr_zero_oci) == "deterministic"


# ---------------------------------------------------------------------------
# Test 4 — boundary: oci exactly at OCI_LOW_CONCENTRATION_THRESHOLD (3.0)
#           oci < threshold is False at equality → typical_concentration
# ---------------------------------------------------------------------------

def test_r1_state_boundary_at_threshold() -> None:
    """r1_state_for returns 'typical_concentration' at oci exactly == threshold.

    The predicate is strict less-than: oci < OCI_LOW_CONCENTRATION_THRESHOLD.
    At equality the condition is False, so the state is typical_concentration.
    """
    wmr = _make_wmr(oci=OCI_LOW_CONCENTRATION_THRESHOLD, deterministic_output=False)
    assert r1_state_for(wmr) == "typical_concentration"


# ---------------------------------------------------------------------------
# Test 5 — basic ranking by csi descending
# ---------------------------------------------------------------------------

def test_top_freelist_terms_basic_ranking() -> None:
    """top_freelist_terms returns items sorted by csi descending."""
    csi_dict = {
        "alpha": _make_csi("alpha", csi=0.5),
        "beta":  _make_csi("beta",  csi=0.9),
        "gamma": _make_csi("gamma", csi=0.3),
        "delta": _make_csi("delta", csi=0.7),
    }
    result = top_freelist_terms(csi_dict)
    assert result == ["beta", "delta", "alpha", "gamma"]


# ---------------------------------------------------------------------------
# Test 6 — k parameter: only k entries returned
# ---------------------------------------------------------------------------

def test_top_freelist_terms_k_parameter() -> None:
    """top_freelist_terms respects the k parameter."""
    csi_dict = {
        "a": _make_csi("a", csi=0.9),
        "b": _make_csi("b", csi=0.8),
        "c": _make_csi("c", csi=0.7),
        "d": _make_csi("d", csi=0.6),
        "e": _make_csi("e", csi=0.5),
        "f": _make_csi("f", csi=0.4),
    }
    result_k3 = top_freelist_terms(csi_dict, k=3)
    assert len(result_k3) == 3
    assert result_k3 == ["a", "b", "c"]

    result_k1 = top_freelist_terms(csi_dict, k=1)
    assert result_k1 == ["a"]


# ---------------------------------------------------------------------------
# Test 7 — stable tie-break: lexicographic ascending on term string
# ---------------------------------------------------------------------------

def test_top_freelist_terms_stable_tiebreak() -> None:
    """top_freelist_terms uses lexicographic ascending tie-break on equal csi."""
    csi_dict = {
        "zebra":  _make_csi("zebra",  csi=0.7),
        "apple":  _make_csi("apple",  csi=0.7),
        "mango":  _make_csi("mango",  csi=0.7),
        "kiwi":   _make_csi("kiwi",   csi=0.5),
    }
    result = top_freelist_terms(csi_dict, k=4)
    # All three 0.7 items appear before 0.4; alphabetical order within tied group.
    assert result == ["apple", "mango", "zebra", "kiwi"]


# ---------------------------------------------------------------------------
# Test 8 — empty input returns empty list
# ---------------------------------------------------------------------------

def test_top_freelist_terms_empty_input() -> None:
    """top_freelist_terms returns [] when the input dict is empty."""
    assert top_freelist_terms({}) == []
    assert top_freelist_terms({}, k=5) == []


# ---------------------------------------------------------------------------
# Test 9 — TOP_TERMS_METRIC constant value is "sutrop_csi"
# ---------------------------------------------------------------------------

def test_top_terms_metric_constant() -> None:
    """TOP_TERMS_METRIC constant must equal 'sutrop_csi' (Q4 binding).

    The Q4 CDA SME ruling binds Sutrop CSI as the canonical salience-rank
    metric for LSB display. This test ensures the constant value is correct
    and that any future change is caught at review time.
    """
    assert TOP_TERMS_METRIC == "sutrop_csi"
    assert DEFAULT_TOP_K == 5


# ---------------------------------------------------------------------------
# Gap-fill tests (Phase 5 T3 Tester verdict — added to complete edge coverage)
# ---------------------------------------------------------------------------

# Gap 1 — top_freelist_terms: k=0 returns empty list
# ---------------------------------------------------------------------------

def test_top_freelist_terms_k_zero_returns_empty() -> None:
    """top_freelist_terms(k=0) returns an empty list even when input is non-empty.

    Python slice semantics: sorted_items[:0] is always []. Exercising this
    ensures callers that pass k=0 get an empty list rather than an error.
    """
    csi_dict = {
        "alpha": _make_csi("alpha", csi=0.9),
        "beta":  _make_csi("beta",  csi=0.7),
    }
    result = top_freelist_terms(csi_dict, k=0)
    assert result == []


# Gap 2 — top_freelist_terms: k > len(input) returns all available terms
# ---------------------------------------------------------------------------

def test_top_freelist_terms_k_exceeds_input_length() -> None:
    """top_freelist_terms with k > len(input) returns all available terms.

    Python slice semantics: sorted_items[:k] when k > len is safe and
    returns all elements. Caller should not need to pre-clamp k.
    """
    csi_dict = {
        "alpha": _make_csi("alpha", csi=0.9),
        "beta":  _make_csi("beta",  csi=0.7),
    }
    result = top_freelist_terms(csi_dict, k=100)
    assert len(result) == 2
    assert result == ["alpha", "beta"]
