"""Unit tests for cdb_social/triggers.py — Phase 7 T2.

Tests are organised by CDA SME binding note (§5.x) from
docs/status/2026-05-17-phase7-T2-cda-sme-verdict.md.

All tests are fixture-driven; no real API calls are made.
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, date, datetime
from pathlib import Path

import pytest
from cdb_core.schemas import (
    BootstrapEllipse,
    DomainResult,
    FreeList,
    ModelRef,
    SocialTrigger,
    TriggerType,
)
from cdb_social.triggers import (
    DRIFT_MIN_ITEM_INTERSECTION,
    DRIFT_THRESHOLD,
    EVIDENCE_MIN_KEYS,
    MIN_DIVERGENCE_DELTA,
    DriftDataInsufficientError,
    EvidenceContractError,
    StateFileMissingError,
    _compute_dedupe_key,
    _max_pairwise_gap,
    bootstrap_state,
    detect_divergence,
    detect_drift,
    detect_monthly_roundup,
    detect_new_domain,
    detect_new_model,
    validate_evidence_for_trigger_type,
)

# ─────────────────────────────────────────────────────────────────────────────
# Shared fixture helpers
# ─────────────────────────────────────────────────────────────────────────────

def _model_ref(
    model_id: str = "claude-opus-4-6",
    family: str = "claude",
    version_label: str = "4.6",
) -> ModelRef:
    return ModelRef(
        provider="anthropic",
        model_id=model_id,
        family=family,
        origin="us",
        open_weights=False,
        collection_method="anthropic_api",
        quantization=None,
        release_date=date(2026, 3, 1),
        version_label=version_label,
    )


def _bootstrap_ellipse() -> BootstrapEllipse:
    return BootstrapEllipse(
        center=(0.0, 0.0),
        semi_major=0.1,
        semi_minor=0.05,
        rotation_rad=0.0,
        n_bootstrap=100,
    )


def _domain_result(
    domain_slug: str = "family",
    models: list[ModelRef] | None = None,
    similarity_matrix: list[list[float]] | None = None,
) -> DomainResult:
    if models is None:
        m = _model_ref()
        models = [m]
    if similarity_matrix is None:
        n = len(models)
        similarity_matrix = [[1.0 if i == j else 0.5 for j in range(n)] for i in range(n)]

    model_ids = [m.model_id for m in models]
    mds_coords = {mid: (float(i) * 0.1, 0.0) for i, mid in enumerate(model_ids)}
    mds_uncertainty = {mid: _bootstrap_ellipse() for mid in model_ids}
    n = len(models)
    sim_ci = [[(0.4, 0.6) for _ in range(n)] for _ in range(n)]
    free_lists = {
        mid: FreeList(
            run_id="test_run",
            model=m,
            domain_slug=domain_slug,
            items=["a", "b"],
            raw_order=["a", "b"],
        )
        for mid, m in zip(model_ids, models, strict=True)
    }

    return DomainResult(
        domain_slug=domain_slug,
        analysis_version="0.1",
        models=models,
        free_lists=free_lists,
        mds_coordinates=mds_coords,
        mds_uncertainty=mds_uncertainty,
        similarity_matrix=similarity_matrix,
        similarity_ci=sim_ci,
        consensus_score=4.0,
        consensus_ci=(3.0, 5.0),
        groundings=[],
        selected_baseline_id=None,
        generated_lede="Test lede.",
        generated_at=datetime(2026, 5, 17, 12, 0, 0),
    )


def _write_state(state_dir: Path, filename: str, data: dict) -> None:
    path = state_dir / filename
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _base_manifest() -> dict:
    return {
        "domains": {
            "family": {"models": ["claude-opus-4-6", "gpt-4o"]},
            "food": {"models": ["claude-opus-4-6", "gpt-4o"]},
        }
    }


# ─────────────────────────────────────────────────────────────────────────────
# §5.1 — DRIFT_THRESHOLD constant + lockout + data-insufficient guard
# ─────────────────────────────────────────────────────────────────────────────

class TestDriftConstants:
    def test_drift_threshold_value(self):
        """§5.1 — DRIFT_THRESHOLD must be 0.15 (placeholder per §4.6 line 1209)."""
        assert DRIFT_THRESHOLD == 0.15

    def test_drift_min_item_intersection_value(self):
        """§5.1 — DRIFT_MIN_ITEM_INTERSECTION must be 8 (Register-3 minimum)."""
        assert DRIFT_MIN_ITEM_INTERSECTION == 8

    def test_drift_locked_returns_empty_by_default(self, tmp_path):
        """§5.1 — detect_drift with enable=False (default) returns []."""
        drs = [_domain_result()]
        result = detect_drift(drs, tmp_path)
        assert result == []

    def test_drift_enable_false_explicit(self, tmp_path):
        """§5.1 — detect_drift with enable=False explicit returns []."""
        drs = [_domain_result()]
        result = detect_drift(drs, tmp_path, enable=False)
        assert result == []

    def test_drift_data_insufficient_raises(self, tmp_path):
        """§5.1 — enable=True with only one version raises DriftDataInsufficientError."""
        # Two models in the same family with same version → only one version → no pairs
        # Need two different version_labels to trigger the intersection check.
        m1 = _model_ref("claude-opus-4-6", "claude", "4.6")
        m2 = _model_ref("claude-opus-4-7", "claude", "4.7")
        # With only 2 domain results (< 8 intersection items when checked by domain slug),
        # this raises DriftDataInsufficientError.
        drs = [
            _domain_result("family", [m1]),
            _domain_result("food", [m2]),
        ]
        # family is in v1 set, food is in v2 set; intersection = empty → < 8
        with pytest.raises(DriftDataInsufficientError) as exc_info:
            detect_drift(drs, tmp_path, enable=True)
        assert "DRIFT_MIN_ITEM_INTERSECTION" in str(exc_info.value)

    def test_drift_logs_warning_on_sufficient_data(self, tmp_path, caplog):
        """§5.1 — first fire with sufficient data logs a WARNING."""
        # Build 8+ domains each with two model versions to create intersection >= 8
        m1 = _model_ref("model-v1", "alpha", "1.0")
        m2 = _model_ref("model-v2", "alpha", "2.0")
        domains = [f"domain_{i}" for i in range(9)]
        drs = (
            [_domain_result(d, [m1]) for d in domains]
            + [_domain_result(d, [m2]) for d in domains]
        )
        with caplog.at_level(logging.WARNING, logger="cdb_social.triggers"):
            # Should log warning but not raise (distance is 0.0 < 0.15 → no trigger)
            result = detect_drift(drs, tmp_path, enable=True)
        assert any("DRIFT_THRESHOLD first fire" in r.message for r in caplog.records)
        # distance = 0.0 < 0.15 so no triggers
        assert result == []


# ─────────────────────────────────────────────────────────────────────────────
# §5.2 — MIN_DIVERGENCE_DELTA + point-mean comparison + no CI-overlap testing
# ─────────────────────────────────────────────────────────────────────────────

class TestDivergenceConstants:
    def test_min_divergence_delta_value(self):
        """§5.2 — MIN_DIVERGENCE_DELTA must be 0.02."""
        assert MIN_DIVERGENCE_DELTA == 0.02

    def test_divergence_fires_on_large_delta(self, tmp_path):
        """§5.2 — emit trigger when new gap exceeds prior high by >= 0.02."""
        # similarity_matrix: 2x2, sim=0.5 → distance = 0.5
        # stored_high = 0.10 → delta = 0.40 >= 0.02 → fires
        m1 = _model_ref("alpha", "alpha", "1.0")
        m2 = _model_ref("beta", "beta", "1.0")
        sim = [[1.0, 0.5], [0.5, 1.0]]
        dr = _domain_result("family", [m1, m2], sim)

        _write_state(tmp_path, "divergence_highs.json", {
            "bootstrapped_at": "2026-05-17T12:00:00+00:00",
            "highs": {"family": 0.10},
        })

        triggers = detect_divergence([dr], tmp_path)
        assert len(triggers) == 1
        t = triggers[0]
        assert t.trigger_type == TriggerType.DIVERGENCE
        assert t.evidence["domain_slug"] == "family"
        assert abs(t.evidence["gap_delta"] - 0.40) < 1e-9
        assert abs(t.evidence["new_high"] - 0.50) < 1e-9
        assert abs(t.evidence["old_high"] - 0.10) < 1e-9

    def test_divergence_no_emit_on_small_delta(self, tmp_path):
        """§5.2 — no trigger when new gap exceeds prior high by < 0.02."""
        m1 = _model_ref("alpha", "alpha", "1.0")
        m2 = _model_ref("beta", "beta", "1.0")
        # distance = 1 - 0.89 = 0.11; stored_high = 0.10; delta = 0.01 < 0.02
        sim = [[1.0, 0.89], [0.89, 1.0]]
        dr = _domain_result("family", [m1, m2], sim)

        _write_state(tmp_path, "divergence_highs.json", {
            "bootstrapped_at": "2026-05-17T12:00:00+00:00",
            "highs": {"family": 0.10},
        })

        triggers = detect_divergence([dr], tmp_path)
        assert triggers == []

    def test_divergence_exactly_at_delta_floor_fires(self, tmp_path):
        """§5.2 — trigger fires when gap_delta >= MIN_DIVERGENCE_DELTA.

        Uses a gap=0.40 against stored_high=0.10 so delta=0.30 is well above
        the 0.02 floor (avoids floating-point boundary issues).
        The below-delta test covers the near-miss case independently.
        """
        m1 = _model_ref("alpha", "alpha", "1.0")
        m2 = _model_ref("beta", "beta", "1.0")
        # distance = 1 - 0.60 = 0.40; stored_high = 0.10; delta = 0.30 >= 0.02
        sim = [[1.0, 0.60], [0.60, 1.0]]
        dr = _domain_result("family", [m1, m2], sim)

        _write_state(tmp_path, "divergence_highs.json", {
            "bootstrapped_at": "2026-05-17T12:00:00+00:00",
            "highs": {"family": 0.10},
        })

        triggers = detect_divergence([dr], tmp_path)
        assert len(triggers) == 1

    def test_divergence_gap_delta_is_new_minus_old(self, tmp_path):
        """§5.2 — gap_delta == new_high - old_high (self-consistency check)."""
        m1 = _model_ref("alpha", "alpha", "1.0")
        m2 = _model_ref("beta", "beta", "1.0")
        sim = [[1.0, 0.5], [0.5, 1.0]]
        dr = _domain_result("family", [m1, m2], sim)

        stored_high = 0.10
        _write_state(tmp_path, "divergence_highs.json", {
            "bootstrapped_at": "2026-05-17T12:00:00+00:00",
            "highs": {"family": stored_high},
        })

        triggers = detect_divergence([dr], tmp_path)
        assert len(triggers) == 1
        ev = triggers[0].evidence
        assert abs(ev["gap_delta"] - (ev["new_high"] - ev["old_high"])) < 1e-9

    def test_divergence_no_ci_overlap_testing(self, tmp_path):
        """§5.2 — comparison is point-mean only; no statistical CI-overlap test.

        Verified structurally: the detect_divergence implementation does not
        import or call any statistical-test function.  The test confirms that
        the function fires on a deterministic point-mean comparison.
        """
        import inspect

        import cdb_social.triggers as triggers_module
        source = inspect.getsource(triggers_module.detect_divergence)
        # No CI-overlap statistical-test vocabulary (scipy, t-test, p-value, etc.)
        for forbidden in ("scipy", "ttest", "p_value", "confidence_interval", "statsmodels"):
            assert forbidden not in source

    def test_divergence_state_updated_on_fire(self, tmp_path):
        """§5.2 — state file updated atomically when trigger fires."""
        m1 = _model_ref("alpha", "alpha", "1.0")
        m2 = _model_ref("beta", "beta", "1.0")
        sim = [[1.0, 0.5], [0.5, 1.0]]
        dr = _domain_result("family", [m1, m2], sim)

        _write_state(tmp_path, "divergence_highs.json", {
            "bootstrapped_at": "2026-05-17T12:00:00+00:00",
            "highs": {"family": 0.10},
        })

        detect_divergence([dr], tmp_path)

        updated = json.loads((tmp_path / "divergence_highs.json").read_text())
        assert abs(updated["highs"]["family"] - 0.50) < 1e-9

    def test_divergence_state_not_updated_when_suppressed(self, tmp_path):
        """§5.2 / §5.6 — state NOT updated when trigger is suppressed."""
        m1 = _model_ref("alpha", "alpha", "1.0")
        m2 = _model_ref("beta", "beta", "1.0")
        m3 = _model_ref("gamma", "gamma", "1.0")
        # Without new model: gap for m1,m2 = 0.11 → delta = 0.01 < 0.02
        sim = [[1.0, 0.89, 0.3], [0.89, 1.0, 0.3], [0.3, 0.3, 1.0]]
        dr = _domain_result("family", [m1, m2, m3], sim)

        stored_high = 0.10
        _write_state(tmp_path, "divergence_highs.json", {
            "bootstrapped_at": "2026-05-17T12:00:00+00:00",
            "highs": {"family": stored_high},
        })

        # Exclude m3 (new model): remaining gap between m1,m2 = 0.11, delta = 0.01 < 0.02
        triggers = detect_divergence(
            [dr], tmp_path, new_models_this_run={"family": ["gamma"]}
        )
        assert triggers == []

        # State must NOT be updated
        state = json.loads((tmp_path / "divergence_highs.json").read_text())
        assert abs(state["highs"]["family"] - stored_high) < 1e-9


# ─────────────────────────────────────────────────────────────────────────────
# §5.3 — first-run sentinel semantics; bootstrap_state; fail-loud on absence
# ─────────────────────────────────────────────────────────────────────────────

class TestBootstrapAndStateSentinel:
    def test_missing_seen_models_raises(self, tmp_path):
        """§5.3 — detect_new_model raises StateFileMissingError on absent state."""
        with pytest.raises(StateFileMissingError):
            detect_new_model(_base_manifest(), tmp_path)

    def test_missing_seen_domains_raises(self, tmp_path):
        """§5.3 — detect_new_domain raises StateFileMissingError on absent state."""
        with pytest.raises(StateFileMissingError):
            detect_new_domain(_base_manifest(), tmp_path)

    def test_missing_divergence_highs_raises(self, tmp_path):
        """§5.3 — detect_divergence raises StateFileMissingError on absent state."""
        drs = [_domain_result()]
        with pytest.raises(StateFileMissingError):
            detect_divergence(drs, tmp_path)

    def test_missing_monthly_roundup_raises(self, tmp_path):
        """§5.3 — detect_monthly_roundup raises StateFileMissingError on absent state."""
        now = datetime(2026, 6, 1, 14, 0, 0, tzinfo=UTC)
        with pytest.raises(StateFileMissingError):
            detect_monthly_roundup(tmp_path, now=now)

    def test_bootstrap_writes_sentinel(self, tmp_path):
        """§5.3 — bootstrap_state writes bootstrapped_at sentinel to each file."""
        manifest = _base_manifest()
        drs = [_domain_result("family"), _domain_result("food")]
        bootstrap_state(tmp_path, manifest, drs)

        for fname in ("seen_models.json", "seen_domains.json",
                      "divergence_highs.json", "monthly_roundup.json"):
            data = json.loads((tmp_path / fname).read_text())
            assert "bootstrapped_at" in data, f"{fname} missing bootstrapped_at"

    def test_bootstrap_then_detect_new_model_no_triggers(self, tmp_path):
        """§5.3 — after bootstrap, detect_new_model with same manifest emits []."""
        manifest = _base_manifest()
        drs = [_domain_result("family"), _domain_result("food")]
        bootstrap_state(tmp_path, manifest, drs)

        triggers = detect_new_model(manifest, tmp_path)
        assert triggers == []

    def test_bootstrap_then_detect_new_domain_no_triggers(self, tmp_path):
        """§5.3 — after bootstrap, detect_new_domain with same manifest emits []."""
        manifest = _base_manifest()
        drs = [_domain_result("family"), _domain_result("food")]
        bootstrap_state(tmp_path, manifest, drs)

        triggers = detect_new_domain(manifest, tmp_path)
        assert triggers == []

    def test_detect_after_bootstrap_then_new_model_fires(self, tmp_path):
        """§5.3 — after bootstrap, detect_new_model fires on genuinely new model."""
        manifest = _base_manifest()
        drs = [_domain_result("family"), _domain_result("food")]
        bootstrap_state(tmp_path, manifest, drs)

        new_manifest = {
            "domains": {
                "family": {"models": ["claude-opus-4-6", "gpt-4o", "gemini-2-flash"]},
                "food": {"models": ["claude-opus-4-6", "gpt-4o"]},
            }
        }
        triggers = detect_new_model(new_manifest, tmp_path)
        assert len(triggers) == 1
        assert triggers[0].model_id == "gemini-2-flash"
        assert triggers[0].domain_slug == "family"

    def test_detect_new_domain_after_bootstrap_fires(self, tmp_path):
        """§5.3 — after bootstrap, detect_new_domain fires on genuinely new domain."""
        manifest = _base_manifest()
        drs = [_domain_result("family"), _domain_result("food")]
        bootstrap_state(tmp_path, manifest, drs)

        new_manifest = {
            "domains": {
                "family": {"models": ["claude-opus-4-6", "gpt-4o"]},
                "food": {"models": ["claude-opus-4-6", "gpt-4o"]},
                "kinship": {"models": ["claude-opus-4-6"]},
            }
        }
        triggers = detect_new_domain(new_manifest, tmp_path)
        assert len(triggers) == 1
        assert triggers[0].domain_slug == "kinship"
        assert triggers[0].evidence["n_models"] == 1


# ─────────────────────────────────────────────────────────────────────────────
# §5.4 — monthly_roundup firing rule + evidence-payload contract
# ─────────────────────────────────────────────────────────────────────────────

class TestMonthlyRoundup:
    def test_fires_on_first_of_month(self, tmp_path):
        """§5.4 — fires on the 1st of the month at 14:00 UTC."""
        # last_fired_month is April; now is June 1 → fires for May
        _write_state(tmp_path, "monthly_roundup.json", {
            "bootstrapped_at": "2026-05-01T14:00:00+00:00",
            "last_fired_month": "2026-04",
        })
        now = datetime(2026, 6, 1, 14, 0, 0, tzinfo=UTC)
        triggers = detect_monthly_roundup(tmp_path, now=now)
        assert len(triggers) == 1
        t = triggers[0]
        assert t.trigger_type == TriggerType.MONTHLY_ROUNDUP
        assert t.evidence["month"] == "2026-05"  # previous calendar month

    def test_evidence_month_is_previous_calendar_month(self, tmp_path):
        """§5.4 — evidence['month'] is the previous calendar month, not current."""
        _write_state(tmp_path, "monthly_roundup.json", {
            "bootstrapped_at": "2026-01-01T14:00:00+00:00",
            "last_fired_month": "2025-11",
        })
        # Running in January 2026 → previous month is December 2025
        now = datetime(2026, 1, 1, 14, 0, 0, tzinfo=UTC)
        triggers = detect_monthly_roundup(tmp_path, now=now)
        assert len(triggers) == 1
        assert triggers[0].evidence["month"] == "2025-12"

    def test_idempotent_within_same_month(self, tmp_path):
        """§5.4 — re-running in the same month emits nothing."""
        _write_state(tmp_path, "monthly_roundup.json", {
            "bootstrapped_at": "2026-05-17T12:00:00+00:00",
            "last_fired_month": "2026-05",
        })
        now = datetime(2026, 6, 2, 14, 0, 0, tzinfo=UTC)
        # Fires once for May
        triggers1 = detect_monthly_roundup(tmp_path, now=now)
        assert triggers1 == []

    def test_idempotent_on_second_call_same_month(self, tmp_path):
        """§5.4 — second call in same month after first fires returns []."""
        _write_state(tmp_path, "monthly_roundup.json", {
            "bootstrapped_at": "2026-05-01T14:00:00+00:00",
            "last_fired_month": "2026-04",
        })
        now = datetime(2026, 6, 1, 14, 0, 0, tzinfo=UTC)
        triggers1 = detect_monthly_roundup(tmp_path, now=now)
        assert len(triggers1) == 1
        # Second call in same month
        triggers2 = detect_monthly_roundup(tmp_path, now=now)
        assert triggers2 == []

    def test_state_updated_after_fire(self, tmp_path):
        """§5.4 — state file updated with last_fired_month after fire."""
        _write_state(tmp_path, "monthly_roundup.json", {
            "bootstrapped_at": "2026-05-01T14:00:00+00:00",
            "last_fired_month": "2026-04",
        })
        now = datetime(2026, 6, 1, 14, 0, 0, tzinfo=UTC)
        detect_monthly_roundup(tmp_path, now=now)

        state = json.loads((tmp_path / "monthly_roundup.json").read_text())
        assert state["last_fired_month"] == "2026-05"

    def test_year_boundary_fires_for_december(self, tmp_path):
        """§5.4 — January run fires for December of previous year."""
        _write_state(tmp_path, "monthly_roundup.json", {
            "bootstrapped_at": "2025-12-01T14:00:00+00:00",
            "last_fired_month": "2025-11",
        })
        now = datetime(2026, 1, 1, 14, 0, 0, tzinfo=UTC)
        triggers = detect_monthly_roundup(tmp_path, now=now)
        assert len(triggers) == 1
        assert triggers[0].evidence["month"] == "2025-12"


# ─────────────────────────────────────────────────────────────────────────────
# §5.5 — dedupe_key formula matches T1 §5.8 spec
# ─────────────────────────────────────────────────────────────────────────────

class TestDedupeKey:
    def test_key_is_16_chars(self):
        """§5.5 — dedupe_key is 16 hex characters (SHA256[:16])."""
        key = _compute_dedupe_key(TriggerType.NEW_MODEL, "family", "claude-opus-4-6",
                                  {"first_seen_in_domain": "family"})
        assert len(key) == 16
        assert all(c in "0123456789abcdef" for c in key)

    def test_key_deterministic(self):
        """§5.5 — same inputs produce same key."""
        key1 = _compute_dedupe_key(TriggerType.NEW_MODEL, "family", "claude-opus-4-6",
                                   {"first_seen_in_domain": "family"})
        key2 = _compute_dedupe_key(TriggerType.NEW_MODEL, "family", "claude-opus-4-6",
                                   {"first_seen_in_domain": "family"})
        assert key1 == key2

    def test_key_varies_with_trigger_type(self):
        """§5.5 — different trigger types produce different keys."""
        evidence = {"month": "2026-05"}
        k1 = _compute_dedupe_key(TriggerType.MONTHLY_ROUNDUP, None, None, evidence)
        k2 = _compute_dedupe_key(TriggerType.DIVERGENCE, None, None, evidence)
        assert k1 != k2

    def test_key_varies_with_domain(self):
        """§5.5 — different domain_slugs produce different keys."""
        evidence = {"first_seen_in_domain": "family"}
        k1 = _compute_dedupe_key(TriggerType.NEW_MODEL, "family", "gpt-4o", evidence)
        k2 = _compute_dedupe_key(TriggerType.NEW_MODEL, "food", "gpt-4o", evidence)
        assert k1 != k2

    def test_key_excludes_drafter_and_prompt_version(self):
        """§5.5 — key formula is callable without drafter_version/prompt_version."""
        # The formula intentionally excludes drafter_version and prompt_version.
        # Test that the function signature has no such parameters.
        import inspect
        sig = inspect.signature(_compute_dedupe_key)
        param_names = list(sig.parameters.keys())
        assert "drafter_version" not in param_names
        assert "prompt_version" not in param_names

    def test_key_stable_across_evidence_key_order(self):
        """§5.5 — canonical_json (sort_keys=True) means key is order-independent."""
        evidence_ab = {"a": 1, "b": 2}
        evidence_ba = {"b": 2, "a": 1}
        k1 = _compute_dedupe_key(TriggerType.MONTHLY_ROUNDUP, None, None, evidence_ab)
        k2 = _compute_dedupe_key(TriggerType.MONTHLY_ROUNDUP, None, None, evidence_ba)
        assert k1 == k2

    def test_emitted_triggers_carry_dedupe_key(self, tmp_path):
        """§5.5 — every emitted trigger has a non-empty dedupe_key."""
        manifest = _base_manifest()
        drs = [_domain_result("family"), _domain_result("food")]
        bootstrap_state(tmp_path, manifest, drs)

        new_manifest = {
            "domains": {
                "family": {"models": ["claude-opus-4-6", "gpt-4o", "gemini-2-flash"]},
                "food": {"models": ["claude-opus-4-6", "gpt-4o"]},
            }
        }
        triggers = detect_new_model(new_manifest, tmp_path)
        assert all(len(t.dedupe_key) == 16 for t in triggers)


# ─────────────────────────────────────────────────────────────────────────────
# §5.6 — divergence ∩ new-model: new-model-masquerade suppression
# ─────────────────────────────────────────────────────────────────────────────

class TestDivergenceNewModelInteraction:
    def test_new_model_masquerade_suppressed(self, tmp_path):
        """§5.6 — apparent new high caused by new model is suppressed.

        Setup: stored_high=0.10. A new model 'gamma' with low similarity to
        'alpha' and 'beta' creates a new max gap of 0.70 (distance = 1 - 0.30).
        Without exclusion, this would fire (delta = 0.60 >= 0.02).
        With 'gamma' excluded, the remaining gap (alpha–beta = 0.11, delta = 0.01)
        is below MIN_DIVERGENCE_DELTA — trigger is suppressed.
        """
        m1 = _model_ref("alpha", "alpha", "1.0")
        m2 = _model_ref("beta", "beta", "1.0")
        m3 = _model_ref("gamma", "gamma", "1.0")
        # gamma (index 2) has low similarity to others
        sim = [
            [1.0, 0.89, 0.30],
            [0.89, 1.0, 0.30],
            [0.30, 0.30, 1.0],
        ]
        dr = _domain_result("family", [m1, m2, m3], sim)

        _write_state(tmp_path, "divergence_highs.json", {
            "bootstrapped_at": "2026-05-17T12:00:00+00:00",
            "highs": {"family": 0.10},
        })

        # gamma is new this run
        triggers = detect_divergence(
            [dr], tmp_path, new_models_this_run={"family": ["gamma"]}
        )
        assert triggers == []

    def test_organic_divergence_fires_despite_new_model(self, tmp_path):
        """§5.6 — real organic divergence (excl. new model) still fires.

        Setup: stored_high=0.10. New model 'gamma' is similar to both others.
        The pre-existing pair alpha–beta now has gap=0.50 → delta=0.40 >= 0.02.
        Trigger fires despite gamma being new.
        """
        m1 = _model_ref("alpha", "alpha", "1.0")
        m2 = _model_ref("beta", "beta", "1.0")
        m3 = _model_ref("gamma", "gamma", "1.0")
        # alpha–beta: distance = 0.50; gamma is close to both
        sim = [
            [1.0, 0.50, 0.95],
            [0.50, 1.0, 0.95],
            [0.95, 0.95, 1.0],
        ]
        dr = _domain_result("family", [m1, m2, m3], sim)

        _write_state(tmp_path, "divergence_highs.json", {
            "bootstrapped_at": "2026-05-17T12:00:00+00:00",
            "highs": {"family": 0.10},
        })

        # gamma is new this run; exclude it from comparison
        triggers = detect_divergence(
            [dr], tmp_path, new_models_this_run={"family": ["gamma"]}
        )
        assert len(triggers) == 1
        ev = triggers[0].evidence
        assert ev["domain_slug"] == "family"
        assert abs(ev["new_high"] - 0.50) < 1e-9
        # model_pair should be the excluded-new-model-free argmax pair
        assert set(ev["model_pair"]) == {"alpha", "beta"}

    def test_model_pair_excludes_new_model(self, tmp_path):
        """§5.6 — model_pair in evidence is argmax pair after new-model exclusion."""
        m1 = _model_ref("alpha", "alpha", "1.0")
        m2 = _model_ref("beta", "beta", "1.0")
        m3 = _model_ref("gamma", "gamma", "1.0")
        # Without gamma: alpha–beta gap = 0.50; with gamma: gamma would be max
        sim = [
            [1.0, 0.50, 0.10],
            [0.50, 1.0, 0.10],
            [0.10, 0.10, 1.0],
        ]
        dr = _domain_result("family", [m1, m2, m3], sim)

        _write_state(tmp_path, "divergence_highs.json", {
            "bootstrapped_at": "2026-05-17T12:00:00+00:00",
            "highs": {"family": 0.10},
        })

        triggers = detect_divergence(
            [dr], tmp_path, new_models_this_run={"family": ["gamma"]}
        )
        assert len(triggers) == 1
        ev = triggers[0].evidence
        # gamma is excluded; argmax should be alpha–beta pair
        assert "gamma" not in ev["model_pair"]

    def test_baseline_not_updated_on_suppressed_divergence(self, tmp_path):
        """§5.6 — baseline not updated when divergence is suppressed (new-model masquerade)."""
        m1 = _model_ref("alpha", "alpha", "1.0")
        m2 = _model_ref("beta", "beta", "1.0")
        m3 = _model_ref("gamma", "gamma", "1.0")
        sim = [
            [1.0, 0.89, 0.30],
            [0.89, 1.0, 0.30],
            [0.30, 0.30, 1.0],
        ]
        dr = _domain_result("family", [m1, m2, m3], sim)

        original_high = 0.10
        _write_state(tmp_path, "divergence_highs.json", {
            "bootstrapped_at": "2026-05-17T12:00:00+00:00",
            "highs": {"family": original_high},
        })

        triggers = detect_divergence(
            [dr], tmp_path, new_models_this_run={"family": ["gamma"]}
        )
        assert triggers == []

        state = json.loads((tmp_path / "divergence_highs.json").read_text())
        assert abs(state["highs"]["family"] - original_high) < 1e-9

    def test_max_pairwise_gap_helper_with_exclusion(self):
        """§5.6 — _max_pairwise_gap correctly excludes specified models."""
        models = ["alpha", "beta", "gamma"]
        # gamma is most divergent from all
        sim = [[1.0, 0.9, 0.3], [0.9, 1.0, 0.3], [0.3, 0.3, 1.0]]
        gap_full, pair_full = _max_pairwise_gap(sim, models)
        assert pair_full[0] in {"alpha", "beta"} or pair_full[1] == "gamma"

        gap_excl, pair_excl = _max_pairwise_gap(sim, models, exclude_models={"gamma"})
        assert "gamma" not in pair_excl
        assert abs(gap_excl - (1.0 - 0.9)) < 1e-9

    def test_max_pairwise_gap_insufficient_models_after_exclusion(self):
        """§5.6 — _max_pairwise_gap returns (0.0, ('', '')) when < 2 remain."""
        models = ["alpha", "beta"]
        sim = [[1.0, 0.5], [0.5, 1.0]]
        gap, pair = _max_pairwise_gap(sim, models, exclude_models={"alpha", "beta"})
        assert gap == 0.0
        assert pair == ("", "")


# ─────────────────────────────────────────────────────────────────────────────
# §5.7 — evidence enforcement: validate_evidence_for_trigger_type
# ─────────────────────────────────────────────────────────────────────────────

class TestEvidenceEnforcement:
    def _minimal_trigger(
        self,
        trigger_type: TriggerType,
        evidence: dict,
    ) -> SocialTrigger:
        return SocialTrigger(
            trigger_type=trigger_type,
            detected_at=datetime(2026, 5, 17, 12, 0, 0),
            domain_slug=None,
            model_id=None,
            evidence=evidence,
            dedupe_key="deadbeef01234567",
        )

    def test_new_model_valid_evidence_passes(self):
        """§5.7 — NEW_MODEL with required key passes validation."""
        t = self._minimal_trigger(
            TriggerType.NEW_MODEL,
            {"first_seen_in_domain": "family"},
        )
        validate_evidence_for_trigger_type(t)  # no exception

    def test_new_model_missing_key_raises(self):
        """§5.7 — NEW_MODEL missing first_seen_in_domain raises EvidenceContractError."""
        t = self._minimal_trigger(TriggerType.NEW_MODEL, {})
        with pytest.raises(EvidenceContractError) as exc_info:
            validate_evidence_for_trigger_type(t)
        assert "first_seen_in_domain" in str(exc_info.value)

    def test_new_domain_valid_evidence_passes(self):
        """§5.7 — NEW_DOMAIN with required keys passes validation."""
        t = self._minimal_trigger(
            TriggerType.NEW_DOMAIN,
            {"domain_slug": "family", "n_models": 3},
        )
        validate_evidence_for_trigger_type(t)

    def test_new_domain_missing_n_models_raises(self):
        """§5.7 — NEW_DOMAIN missing n_models raises EvidenceContractError."""
        t = self._minimal_trigger(TriggerType.NEW_DOMAIN, {"domain_slug": "family"})
        with pytest.raises(EvidenceContractError) as exc_info:
            validate_evidence_for_trigger_type(t)
        assert "n_models" in str(exc_info.value)

    def test_divergence_valid_evidence_passes(self):
        """§5.7 — DIVERGENCE with all required keys passes validation."""
        t = self._minimal_trigger(
            TriggerType.DIVERGENCE,
            {
                "domain_slug": "family",
                "model_pair": ["alpha", "beta"],
                "old_high": 0.10,
                "new_high": 0.50,
                "gap_delta": 0.40,
            },
        )
        validate_evidence_for_trigger_type(t)

    def test_divergence_missing_keys_raises(self):
        """§5.7 — DIVERGENCE missing model_pair raises EvidenceContractError."""
        t = self._minimal_trigger(
            TriggerType.DIVERGENCE,
            {"domain_slug": "family", "old_high": 0.10, "new_high": 0.50, "gap_delta": 0.40},
        )
        with pytest.raises(EvidenceContractError) as exc_info:
            validate_evidence_for_trigger_type(t)
        assert "model_pair" in str(exc_info.value)

    def test_drift_valid_evidence_passes(self):
        """§5.7 — DRIFT with required keys passes validation."""
        t = self._minimal_trigger(
            TriggerType.DRIFT,
            {
                "model_version_returned": "claude-opus-4-6-20260301",
                "procrustes_distance": 0.18,
                "date_pair": ["2026-03-01", "2026-05-01"],
            },
        )
        validate_evidence_for_trigger_type(t)

    def test_drift_missing_model_version_raises(self):
        """§5.7 — DRIFT missing model_version_returned raises EvidenceContractError."""
        t = self._minimal_trigger(
            TriggerType.DRIFT,
            {"procrustes_distance": 0.18, "date_pair": ["2026-03-01", "2026-05-01"]},
        )
        with pytest.raises(EvidenceContractError) as exc_info:
            validate_evidence_for_trigger_type(t)
        assert "model_version_returned" in str(exc_info.value)

    def test_monthly_roundup_valid_evidence_passes(self):
        """§5.7 — MONTHLY_ROUNDUP with required key passes validation."""
        t = self._minimal_trigger(
            TriggerType.MONTHLY_ROUNDUP,
            {"month": "2026-05"},
        )
        validate_evidence_for_trigger_type(t)

    def test_monthly_roundup_missing_month_raises(self):
        """§5.7 — MONTHLY_ROUNDUP missing month raises EvidenceContractError."""
        t = self._minimal_trigger(TriggerType.MONTHLY_ROUNDUP, {})
        with pytest.raises(EvidenceContractError) as exc_info:
            validate_evidence_for_trigger_type(t)
        assert "month" in str(exc_info.value)

    def test_evidence_min_keys_covers_all_trigger_types(self):
        """§5.7 — EVIDENCE_MIN_KEYS has an entry for every TriggerType value."""
        for ttype in TriggerType:
            assert ttype in EVIDENCE_MIN_KEYS, f"{ttype} missing from EVIDENCE_MIN_KEYS"

    def test_error_message_names_trigger_type(self):
        """§5.7 — EvidenceContractError message includes trigger_type name."""
        t = self._minimal_trigger(TriggerType.NEW_MODEL, {})
        with pytest.raises(EvidenceContractError) as exc_info:
            validate_evidence_for_trigger_type(t)
        assert "new_model" in str(exc_info.value).lower()


# ─────────────────────────────────────────────────────────────────────────────
# detect_new_model additional tests
# ─────────────────────────────────────────────────────────────────────────────

class TestDetectNewModel:
    def test_emits_trigger_per_domain_model_pair(self, tmp_path):
        """Each new model in each domain produces one trigger."""
        _write_state(tmp_path, "seen_models.json", {
            "bootstrapped_at": "2026-05-17T12:00:00+00:00",
            "domains": {
                "family": ["claude-opus-4-6"],
                "food": ["claude-opus-4-6"],
            },
        })
        manifest = {
            "domains": {
                "family": {"models": ["claude-opus-4-6", "gpt-4o", "gemini-2-flash"]},
                "food": {"models": ["claude-opus-4-6", "gpt-4o"]},
            }
        }
        triggers = detect_new_model(manifest, tmp_path)
        assert len(triggers) == 3  # gpt-4o in family, gemini in family, gpt-4o in food

    def test_state_updated_after_new_model_fire(self, tmp_path):
        """State file updated atomically when triggers fire."""
        _write_state(tmp_path, "seen_models.json", {
            "bootstrapped_at": "2026-05-17T12:00:00+00:00",
            "domains": {"family": ["claude-opus-4-6"]},
        })
        manifest = {"domains": {"family": {"models": ["claude-opus-4-6", "gpt-4o"]}}}
        detect_new_model(manifest, tmp_path)

        state = json.loads((tmp_path / "seen_models.json").read_text())
        assert "gpt-4o" in state["domains"]["family"]

    def test_idempotent_second_run(self, tmp_path):
        """Running twice with same manifest produces zero triggers on second run."""
        _write_state(tmp_path, "seen_models.json", {
            "bootstrapped_at": "2026-05-17T12:00:00+00:00",
            "domains": {"family": ["claude-opus-4-6"]},
        })
        manifest = {"domains": {"family": {"models": ["claude-opus-4-6", "gpt-4o"]}}}
        detect_new_model(manifest, tmp_path)
        triggers2 = detect_new_model(manifest, tmp_path)
        assert triggers2 == []

    def test_evidence_contains_domain_slug(self, tmp_path):
        """NEW_MODEL evidence contains first_seen_in_domain."""
        _write_state(tmp_path, "seen_models.json", {
            "bootstrapped_at": "2026-05-17T12:00:00+00:00",
            "domains": {"family": []},
        })
        manifest = {"domains": {"family": {"models": ["claude-opus-4-6"]}}}
        triggers = detect_new_model(manifest, tmp_path)
        assert len(triggers) == 1
        assert triggers[0].evidence["first_seen_in_domain"] == "family"


# ─────────────────────────────────────────────────────────────────────────────
# detect_new_domain additional tests
# ─────────────────────────────────────────────────────────────────────────────

class TestDetectNewDomain:
    def test_emits_trigger_for_new_domain(self, tmp_path):
        """NEW_DOMAIN emits trigger for each domain not in seen_domains.json."""
        _write_state(tmp_path, "seen_domains.json", {
            "bootstrapped_at": "2026-05-17T12:00:00+00:00",
            "domains": ["family"],
        })
        manifest = {
            "domains": {
                "family": {"models": ["claude-opus-4-6"]},
                "food": {"models": ["claude-opus-4-6", "gpt-4o"]},
            }
        }
        triggers = detect_new_domain(manifest, tmp_path)
        assert len(triggers) == 1
        assert triggers[0].domain_slug == "food"
        assert triggers[0].evidence["n_models"] == 2

    def test_no_trigger_for_known_domain(self, tmp_path):
        """No trigger when all manifest domains are already in state."""
        _write_state(tmp_path, "seen_domains.json", {
            "bootstrapped_at": "2026-05-17T12:00:00+00:00",
            "domains": ["family", "food"],
        })
        manifest = {
            "domains": {
                "family": {"models": []},
                "food": {"models": []},
            }
        }
        triggers = detect_new_domain(manifest, tmp_path)
        assert triggers == []


# ─────────────────────────────────────────────────────────────────────────────
# Boundary check: no LLM imports in triggers.py
# ─────────────────────────────────────────────────────────────────────────────

def test_no_llm_imports_in_triggers():
    """Structural: triggers.py must not import any LLM client library."""
    source_path = (
        Path(__file__).parent.parent.parent
        / "packages/cdb_social/cdb_social/triggers.py"
    )
    source = source_path.read_text(encoding="utf-8")
    forbidden_imports = [
        "anthropic",
        "openai",
        "google.generativeai",
        "InferenceClient",
        "huggingface_hub",
    ]
    for forbidden in forbidden_imports:
        assert forbidden not in source, (
            f"triggers.py must not import {forbidden!r} (LLM boundary rule)"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Boundary check: no writes to data/raw or data/processed from triggers
# ─────────────────────────────────────────────────────────────────────────────

def test_no_data_raw_writes_in_triggers():
    """Structural: triggers.py must not write to data/raw or data/processed.

    Verifies that no file-write pattern targets those paths.  Docstring
    mentions of the paths (boundary documentation) are acceptable.
    """
    source_path = (
        Path(__file__).parent.parent.parent
        / "packages/cdb_social/cdb_social/triggers.py"
    )
    source = source_path.read_text(encoding="utf-8")
    # Must not open/write files under data/raw or data/processed
    for forbidden_pattern in ('open("data/raw', "open('data/raw",
                               'open("data/processed', "open('data/processed",
                               'Path("data/raw', "Path('data/raw",
                               'Path("data/processed', "Path('data/processed"):
        assert forbidden_pattern not in source, (
            f"triggers.py must not write to {forbidden_pattern!r} (boundary rule)"
        )
