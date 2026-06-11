"""PROMOTE-FOOD-V02: T1 contract tests for food v0.2 promotion.

Tests:
  T1a - consensus_type_override is present and set to WEAK_CONSENSUS in
        data/results/food/0.2.json.
  T1b - auto-derived consensus_type is retained as STRONG_CONSENSUS (audit trail).
  T1c - F3-R3-B override reason string is byte-identical to the CDA SME binding string.
  T1d - centrality_ci is populated for all 12 mode-coherent models (Remedy B contract).
  T1e - similarity_matrix is 12x12 (maverick excluded from similarity basis).
  T1f - generate_lede returns the F3-R3-A string byte-identical for food v0.2 result.
  T1g - DomainResult schema accepts the override fields without validation error.

No real API calls. No rebaseline_corpus run (T1 bytecode contract documents the
seed-reproducibility claim; actual rerun requires the full corpus at data/raw/).
Per CLAUDE.md §9 rule 9.

Source:
  .claude/agent-memory/cda_sme/project_phase9b_food_guard_trip.md round 3
  PROMOTE-FOOD-V02 plan §4 acceptance criteria T1-T3
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from cdb_core.schemas import DomainResult
from cdb_publish.lede import generate_lede

# F3-R3-A verbatim (CDA SME binding). Any edit requires a fresh SME pass.
F3_R3_A = (
    "The food domain shows broad agreement across the 12-model slate. The"
    " point estimate sits comfortably on the strong-consensus side of our"
    " threshold, but the uncertainty band crosses it. The honest read is"
    " that the strength of agreement is not nailed down at this collection"
    " width."
)

# F3-R3-B verbatim (CDA SME binding). Any edit requires a fresh SME pass.
F3_R3_B = (
    "Point estimate is on the strong-consensus side of the 5.0 threshold;"
    " the 95 percent bootstrap interval crosses 5.0. We publish the"
    " conservative classification and disclose the indeterminacy rather than"
    " claim a category the uncertainty does not support."
)

FOOD_RESULT_PATH = (
    Path(__file__).parent.parent.parent
    / "data"
    / "results"
    / "food"
    / "0.2.json"
)


@pytest.fixture(scope="module")
def food_raw() -> dict:
    """Load the promoted food v0.2 result JSON."""
    with open(FOOD_RESULT_PATH) as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def food_result(food_raw: dict) -> DomainResult:
    """Parse the food v0.2 result as a DomainResult (schema validation)."""
    return DomainResult.model_validate(food_raw)


class TestT1SchemaAndOverride:
    """T1 contract: override fields, auto-derived fields, schema validation."""

    def test_t1a_override_field_is_weak_consensus(self, food_raw: dict) -> None:
        """T1a: consensus_type_override is WEAK_CONSENSUS in the promoted JSON."""
        assert food_raw.get("consensus_type_override") == "WEAK_CONSENSUS", (
            "consensus_type_override must be WEAK_CONSENSUS (R1)"
        )

    def test_t1b_auto_derived_retained_as_strong(self, food_raw: dict) -> None:
        """T1b: auto-derived consensus_type is STRONG_CONSENSUS (audit trail, R1)."""
        assert food_raw.get("consensus_type") == "STRONG_CONSENSUS", (
            "Auto-derived consensus_type must remain STRONG_CONSENSUS for audit trail"
        )

    def test_t1c_override_reason_f3_r3_b_byte_identical(self, food_raw: dict) -> None:
        """T1c: consensus_type_override_reason is byte-identical to F3-R3-B."""
        actual = food_raw.get("consensus_type_override_reason", "")
        assert actual == F3_R3_B, (
            f"override_reason does not match F3-R3-B byte-for-byte.\n"
            f"Expected: {F3_R3_B!r}\n"
            f"Got:      {actual!r}"
        )

    def test_t1d_centrality_ci_populated_for_12_models(self, food_raw: dict) -> None:
        """T1d: centrality_ci has 12 entries (Remedy B contract, R2)."""
        centrality_ci = food_raw.get("centrality_ci", {})
        assert len(centrality_ci) == 12, (
            f"centrality_ci must have 12 entries for the 12 mode-coherent models; "
            f"got {len(centrality_ci)}"
        )

    def test_t1e_similarity_matrix_is_12x12(self, food_raw: dict) -> None:
        """T1e: similarity_matrix is 12x12 (maverick excluded, R6)."""
        sim = food_raw.get("similarity_matrix", [])
        assert len(sim) == 12, f"Expected 12 rows, got {len(sim)}"
        for i, row in enumerate(sim):
            assert len(row) == 12, f"Row {i} has {len(row)} columns, expected 12"

    def test_t1f_generate_lede_f3_r3_a_byte_identical(
        self, food_result: DomainResult
    ) -> None:
        """T1f: generate_lede returns F3-R3-A verbatim for food v0.2."""
        lede = generate_lede(food_result)
        assert lede == F3_R3_A, (
            f"generate_lede does not produce F3-R3-A byte-for-byte.\n"
            f"Expected: {F3_R3_A!r}\n"
            f"Got:      {lede!r}"
        )

    def test_t1g_schema_accepts_override_fields(self, food_raw: dict) -> None:
        """T1g: DomainResult parses the promoted JSON without validation error."""
        result = DomainResult.model_validate(food_raw)
        assert result.consensus_type_override == "WEAK_CONSENSUS"
        assert result.consensus_type == "STRONG_CONSENSUS"

    def test_t1h_no_em_dash_in_override_reason(self, food_raw: dict) -> None:
        """T1h: no U+2014 em-dash in override reason (CLAUDE.md hard rule)."""
        reason = food_raw.get("consensus_type_override_reason", "")
        assert "—" not in reason, "Em-dash found in consensus_type_override_reason"

    def test_t1i_maverick_absent_from_centrality(self, food_raw: dict) -> None:
        """T1i: meta-llama/llama-4-maverick is not in cultural_centrality_scores."""
        scores = food_raw.get("cultural_centrality_scores", {})
        assert "meta-llama/llama-4-maverick" not in scores, (
            "maverick must not appear in cultural_centrality_scores (mode-coherent)"
        )

    def test_t1j_maverick_absent_from_mds_coordinates(self, food_raw: dict) -> None:
        """T1j: meta-llama/llama-4-maverick is not in mds_coordinates."""
        mds = food_raw.get("mds_coordinates", {})
        assert "meta-llama/llama-4-maverick" not in mds, (
            "maverick must not appear in mds_coordinates (mode-coherent)"
        )

    def test_t1k_maverick_present_in_models_list(self, food_raw: dict) -> None:
        """T1k: meta-llama/llama-4-maverick is still in models list (R6 / R7)."""
        model_ids = [m["model_id"] for m in food_raw.get("models", [])]
        assert "meta-llama/llama-4-maverick" in model_ids, (
            "maverick must remain in models list for within-model / pooled views"
        )

    def test_t1l_romney_small_n_warning_true(self, food_raw: dict) -> None:
        """T1l: romney_small_n_warning is True for n=12 < 15 threshold."""
        assert food_raw.get("romney_small_n_warning") is True

    def test_t1m_schema_defaults_are_optional(self) -> None:
        """T1m: new fields have falsy defaults (non-breaking schema addition)."""
        # Create minimal DomainResult-like instance via import of a fixture-based
        # approach. Test that the defaults parse without providing the new fields.
        # We check defaults directly via the schema.
        from cdb_core.schemas import DomainResult as DR
        fields = DR.model_fields
        assert "consensus_type_override" in fields
        assert "consensus_type_override_reason" in fields
        # Default for override is None, for reason is ""
        assert fields["consensus_type_override"].default is None
        assert fields["consensus_type_override_reason"].default == ""
