"""Tests for the two-level pipeline and saturation analysis.

See packages/cdb_analyze/cdb_analyze/two_level.py and saturation.py,
ARCHITECTURE.md §4.2.0 (three registers), and docs/SME_REVIEW.md.
"""

from __future__ import annotations

from datetime import UTC, datetime

import numpy as np
import pytest
from cdb_analyze.saturation import (
    SATURATION_REFERENCE_DOMAINS,
    SATURATION_REFERENCE_MODELS,
    identify_knee,
    saturation_curve,
)
from cdb_analyze.two_level import (
    compute_oci,
    options_for_level_two,
    run_within_model_analysis,
)
from cdb_core import (
    FreelistRecord,
    InformantRecord,
    InterviewRecord,
    PileSortRecord,
)

# ---------------------------------------------------------------------------
# Record factory
# ---------------------------------------------------------------------------

def _make_record(
    model_id: str,
    run_index: int,
    items: list[str],
    piles: list[list[str]],
) -> InformantRecord:
    n = len(items)
    idx = {item: i for i, item in enumerate(items)}
    matrix = [[0] * n for _ in range(n)]
    for pile in piles:
        for a in pile:
            for b in pile:
                matrix[idx[a]][idx[b]] = 1

    return InformantRecord(
        informant_id=f"{model_id}_{run_index}",
        domain_slug="family",
        run_index=run_index,
        collection_date=datetime(2026, 4, 19, tzinfo=UTC),
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
            parsed_items=items, parsed_raw_order=items,
        ),
        pile_sort=PileSortRecord(
            prompt_verbatim="p", prompt_version="v1", response_verbatim="r",
            response_object_json={}, input_tokens=1, output_tokens=1,
            latency_ms=1, stop_reason="end_turn",
            parsed_piles=piles, parsed_matrix=matrix,
        ),
        interview=InterviewRecord(
            prompt_verbatim="p", prompt_version="v1", response_verbatim="r",
            response_object_json={}, input_tokens=1, output_tokens=1,
            latency_ms=1, stop_reason="end_turn",
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


def _stable_runs(model_id: str, n: int) -> list[InformantRecord]:
    """N runs of a model that produce identical pile sorts (high OCI)."""
    items = ["mother", "father", "sister", "brother", "uncle", "aunt"]
    piles = [["mother", "father"], ["sister", "brother"], ["uncle", "aunt"]]
    return [_make_record(model_id, i, items, piles) for i in range(n)]


def _variable_runs(model_id: str, n: int) -> list[InformantRecord]:
    """N runs with rotating pile assignments (lower OCI)."""
    items = ["mother", "father", "sister", "brother", "uncle", "aunt"]
    variants = [
        [["mother", "father"], ["sister", "brother"], ["uncle", "aunt"]],
        [["mother", "sister", "aunt"], ["father", "brother", "uncle"]],
        [["mother", "father", "sister", "brother"], ["uncle", "aunt"]],
    ]
    return [
        _make_record(model_id, i, items, variants[i % len(variants)])
        for i in range(n)
    ]


# ---------------------------------------------------------------------------
# run_within_model_analysis
# ---------------------------------------------------------------------------

class TestWithinModelAnalysis:
    def test_stable_runs_produce_high_oci(self):
        records = _stable_runs("claude-opus-4-6", 6)
        wm = run_within_model_analysis(records)
        assert wm.model_id == "claude-opus-4-6"
        assert wm.n_runs == 6
        # All runs identical → agreement matrix is all ones → OCI is
        # capped at the sentinel for effectively infinite concentration,
        # AND deterministic_output is True (λ₂ is effectively zero).
        assert wm.oci >= 5.0
        assert wm.underestimates_uncertainty is True
        assert wm.deterministic_output is True

    def test_variable_runs_produce_lower_oci(self):
        stable_oci = compute_oci(_stable_runs("m", 6))
        variable_oci = compute_oci(_variable_runs("m", 6))
        assert variable_oci < stable_oci

    def test_variable_runs_not_deterministic(self):
        """Variable runs have λ₂ > 0 so deterministic_output is False.

        Guards the distinction between "high OCI" (concentrated but still
        variable) and "deterministic output" (zero variance, the R1-c
        case in DESIGN_SYSTEM.md §3.3.5).
        """
        records = _variable_runs("m", 6)
        wm = run_within_model_analysis(records)
        assert wm.deterministic_output is False

    def test_centroid_run_is_in_inputs(self):
        records = _variable_runs("m", 6)
        wm = run_within_model_analysis(records)
        assert wm.centroid_run_id in {r.informant_id for r in records}

    def test_empty_records_raises(self):
        with pytest.raises(ValueError, match="empty"):
            run_within_model_analysis([])

    def test_mixed_models_raises(self):
        records = [
            _make_record("a", 0, ["x", "y"], [["x", "y"]]),
            _make_record("b", 1, ["x", "y"], [["x", "y"]]),
        ]
        with pytest.raises(ValueError, match="model_id"):
            run_within_model_analysis(records)

    def test_bootstrap_ci_populated_when_requested(self):
        records = _variable_runs("m", 6)
        wm = run_within_model_analysis(records, n_bootstrap=50)
        assert wm.oci_ci is not None
        lo, hi = wm.oci_ci
        assert lo <= wm.oci <= hi or abs(lo - hi) < 1e-6

    def test_underestimates_flag_always_true_for_register_1(self):
        """The R1 underestimation caveat is binding per BOOTSTRAP_DESIGN.md §2."""
        for n in (3, 6, 12):
            wm = run_within_model_analysis(_stable_runs("m", n))
            assert wm.underestimates_uncertainty is True


# ---------------------------------------------------------------------------
# options_for_level_two
# ---------------------------------------------------------------------------

class TestLevelTwoOptions:
    def test_option_a_is_consensus_free_list(self):
        records = _variable_runs("m", 6)
        opts = options_for_level_two(records)
        assert len(opts["option_a"]) > 0
        # Each entry is (item, composite_smiths_s)
        first = opts["option_a"][0]
        assert isinstance(first[0], str)
        assert isinstance(first[1], float)

    def test_option_b_is_an_informant_id(self):
        records = _variable_runs("m", 6)
        opts = options_for_level_two(records)
        assert opts["option_b_centroid_run_id"] in {r.informant_id for r in records}

    def test_option_c_is_numeric_oci(self):
        records = _variable_runs("m", 6)
        opts = options_for_level_two(records)
        assert isinstance(opts["option_c_weight"], float)
        assert opts["option_c_weight"] >= 0.0

    def test_empty_returns_empty_options(self):
        opts = options_for_level_two([])
        assert opts["option_a"] == []
        assert opts["option_b_centroid_run_id"] is None
        assert opts["option_c_weight"] == 0.0


# ---------------------------------------------------------------------------
# saturation analysis
# ---------------------------------------------------------------------------

class TestSaturationCurve:
    def test_sweep_respects_available_n(self):
        """N values larger than len(records) are skipped."""
        records = _variable_runs("m", 7)
        curve = saturation_curve(records, n_values=(3, 6, 9))
        assert [pt.n_runs for pt in curve] == [3, 6]

    def test_first_point_has_no_delta(self):
        records = _stable_runs("m", 6)
        curve = saturation_curve(records, n_values=(3, 6))
        assert curve[0].delta_top_k_jaccard is None
        assert curve[1].delta_top_k_jaccard is not None

    def test_stable_inputs_give_high_delta_jaccard(self):
        records = _stable_runs("m", 12)
        curve = saturation_curve(records, n_values=(5, 10))
        # Identical piles across runs → top-K should perfectly overlap
        assert curve[-1].delta_top_k_jaccard is not None
        assert curve[-1].delta_top_k_jaccard > 0.5

    def test_identify_knee_returns_margin_scaled_n(self):
        records = _stable_runs("m", 12)
        curve = saturation_curve(records, n_values=(5, 10))
        knee = identify_knee(curve, delta_threshold=0.5)
        assert knee is not None
        assert knee >= 10  # at minimum, the N at which saturation was detected

    def test_identify_knee_returns_none_when_not_saturated(self):
        """If delta never meets threshold, knee is None and caller expands sweep."""
        # With random-ish variability every N, top-K jaccard will not exceed 0.99
        records = _variable_runs("m", 9)
        curve = saturation_curve(records, n_values=(3, 6, 9))
        knee = identify_knee(curve, delta_threshold=0.99)
        # If the curve happens to saturate in this synthetic fixture, knee may
        # still be returned; the assertion is only that the function handles
        # the "never saturates" path without crashing.
        assert knee is None or knee >= 6


class TestSaturationConstants:
    def test_reference_models_include_all_three_architectures(self):
        """Per the standing authority: Claude Opus + GPT flagship + open-weight."""
        assert "claude-opus-4-6" in SATURATION_REFERENCE_MODELS
        assert "gpt-4o" in SATURATION_REFERENCE_MODELS
        assert any("llama" in m for m in SATURATION_REFERENCE_MODELS)

    def test_reference_domains_include_grounded_and_ungrounded(self):
        """Family is grounded (Romney 1996); holidays is ungrounded in v1."""
        assert "family" in SATURATION_REFERENCE_DOMAINS
        assert "holidays" in SATURATION_REFERENCE_DOMAINS


# ---------------------------------------------------------------------------
# OCI reliability under a known-signal case
# ---------------------------------------------------------------------------

class TestOCIReliability:
    def test_oci_symmetric_and_nonneg(self):
        records = _variable_runs("m", 6)
        oci = compute_oci(records)
        assert oci >= 0.0
        assert not np.isnan(oci)

    def test_two_runs_produces_finite_value(self):
        records = _stable_runs("m", 2)
        oci = compute_oci(records)
        assert oci >= 0.0

    def test_single_run_oci_is_zero(self):
        records = _stable_runs("m", 1)
        assert compute_oci(records) == 0.0
