"""Unit tests for scripts/run_phase4b_variance.py.

Tests cover:
1. Run-plan generator: 20 × 9 × 5 × 2 = 1,800 cells with correct field combinations.
2. Resume logic: a triple with 5/5 existing records is skipped.
3. Preflight-skip logic: models on a quota-exhausted provider are dropped from the plan.
4. Success-rate computation against a small fixture corpus.

No real API calls. No LLM imports. Fixtures are synthetic inline dicts.

References:
    Phase 4b architect plan §8 T4:
        docs/status/2026-05-07-phase4b-architect-plan.md
    SME plan verdict P2, P5:
        docs/status/2026-05-07-phase4b-cda-sme-plan-verdict.md
    CLAUDE.md §6 R9: no real API calls in tests.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

# ---------------------------------------------------------------------------
# Import the module under test
# ---------------------------------------------------------------------------

_SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

# We must patch the collect module's MODEL_REGISTRY before importing the target
# so that we can control it in tests.
#
# Strategy: import after patching at the module level; use importlib for
# a clean re-import in each test function that needs specific registry state.

# ---------------------------------------------------------------------------
# Helpers — build minimal fixture records
# ---------------------------------------------------------------------------

def _make_informant_jsonl_line(
    model_id: str,
    prompt_version: str,
    domain_slug: str,
    run_index: int,
    campaign_id: str,
    qa_passed: bool = True,
) -> str:
    """Return a minimal JSON line representing one InformantRecord."""
    qa_notes = f"campaign_id={campaign_id}"
    record = {
        "informant_id": f"test_{model_id}_{prompt_version}_{domain_slug}_{run_index}",
        "domain_slug": domain_slug,
        "run_index": run_index,
        "model_id": model_id,
        "model_version_returned": f"{model_id}-returned",
        "family": "test",
        "provider": "openrouter",
        "provider_request_id": f"req_{run_index}",
        "open_weights": False,
        "origin_country": "us",
        "collection_method": "openrouter",
        "collection_mode": "single_pass",
        "api_endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "api_version": "",
        "temperature": 0.7,
        "input_tokens": 100,
        "output_tokens": 50,
        "freelist": {
            "prompt_verbatim": "test prompt",
            "prompt_version": prompt_version,
            "response_verbatim": "1. item_a\n2. item_b",
            "response_object_json": {},
            "input_tokens": 100,
            "output_tokens": 50,
            "latency_ms": 500,
            "stop_reason": "end_turn",
            "parsed_items": ["item_a", "item_b"],
            "parsed_raw_order": ["item_a", "item_b"],
        },
        "pile_sort": {
            "prompt_verbatim": "test sort prompt",
            "prompt_version": prompt_version,
            "response_verbatim": "{}",
            "response_object_json": {},
            "input_tokens": 50,
            "output_tokens": 20,
            "latency_ms": 300,
            "stop_reason": "end_turn",
            "parsed_piles": [["item_a"], ["item_b"]],
            "parsed_matrix": [[1, 0], [0, 1]],
            "item_source": "own_freelist",
        },
        "interview": {
            "prompt_verbatim": "test interview prompt",
            "prompt_version": prompt_version,
            "response_verbatim": "pile 1: label1\npile 2: label2",
            "response_object_json": {},
            "input_tokens": 30,
            "output_tokens": 10,
            "latency_ms": 200,
            "stop_reason": "end_turn",
            "parsed_pile_labels": ["label1", "label2"],
        },
        "sha256_manifest": "abcdef1234567890",
        "qa_passed": qa_passed,
        "qa_notes": qa_notes,
    }
    return json.dumps(record)


def _make_failure_jsonl_line(
    model_id: str,
    prompt_version: str,
    domain_slug: str,
    run_index: int,
    campaign_id: str,
) -> str:
    """Return a minimal JSON line representing one failure row."""
    record = {
        "timestamp": "2026-05-08T10:00:00",
        "error_type": "ValueError",
        "error_message": "Test failure",
        "context": {
            "model_id": model_id,
            "domain": domain_slug,
            "run_index": run_index,
            "prompt_version": prompt_version,
            "campaign_id": campaign_id,
        },
    }
    return json.dumps(record)


# ---------------------------------------------------------------------------
# Test 1: run-plan generator produces 1,800 cells
# ---------------------------------------------------------------------------

def test_run_plan_full_size():
    """build_run_plan with no completed cells produces exactly 1,800 cells."""
    # Import locally to avoid module-level side effects
    from run_phase4b_variance import (
        N_RUNS_PER_CELL,
        VARIANCE_DOMAINS,
        VARIANCE_MODEL_IDS,
        VARIANCE_PROMPT_VERSIONS,
        build_run_plan,
    )

    expected_count = (
        len(VARIANCE_MODEL_IDS)
        * len(VARIANCE_PROMPT_VERSIONS)
        * N_RUNS_PER_CELL
        * len(VARIANCE_DOMAINS)
    )
    assert expected_count == 1800, (
        f"Expected 1800 cells (20×9×5×2) but computed {expected_count}"
    )

    completed_counts: dict = {}
    plan = build_run_plan(VARIANCE_MODEL_IDS, completed_counts)
    assert len(plan) == 1800


def test_run_plan_correct_models():
    """Plan contains exactly the 20 expected model_ids."""
    from run_phase4b_variance import VARIANCE_MODEL_IDS, build_run_plan

    plan = build_run_plan(VARIANCE_MODEL_IDS, {})
    plan_models = {cell.model_id for cell in plan}
    assert plan_models == set(VARIANCE_MODEL_IDS)


def test_run_plan_correct_variants():
    """Plan contains exactly the 9 expected prompt versions."""
    from run_phase4b_variance import VARIANCE_MODEL_IDS, VARIANCE_PROMPT_VERSIONS, build_run_plan

    plan = build_run_plan(VARIANCE_MODEL_IDS, {})
    plan_versions = {cell.prompt_version for cell in plan}
    assert plan_versions == set(VARIANCE_PROMPT_VERSIONS)


def test_run_plan_correct_domains():
    """Plan contains exactly the 2 expected domains."""
    from run_phase4b_variance import VARIANCE_DOMAINS, VARIANCE_MODEL_IDS, build_run_plan

    plan = build_run_plan(VARIANCE_MODEL_IDS, {})
    plan_domains = {cell.domain for cell in plan}
    assert plan_domains == set(VARIANCE_DOMAINS)


def test_run_plan_correct_run_indices():
    """For a single model/variant/domain triple, run indices are 0..4."""
    from run_phase4b_variance import VARIANCE_MODEL_IDS, build_run_plan

    plan = build_run_plan(VARIANCE_MODEL_IDS, {})
    mid = VARIANCE_MODEL_IDS[0]
    pv = "v1_s1"
    domain = "family"
    triple_cells = sorted(
        [c for c in plan if c.model_id == mid and c.prompt_version == pv and c.domain == domain],
        key=lambda c: c.run_index,
    )
    assert len(triple_cells) == 5
    assert [c.run_index for c in triple_cells] == [0, 1, 2, 3, 4]


def test_run_plan_v2_soft1_included():
    """v2_soft1 is one of the 9 variants and appears in the plan."""
    from run_phase4b_variance import VARIANCE_MODEL_IDS, build_run_plan

    plan = build_run_plan(VARIANCE_MODEL_IDS, {})
    v2_cells = [c for c in plan if c.prompt_version == "v2_soft1"]
    # 20 models × 5 runs × 2 domains = 200 v2_soft1 cells
    assert len(v2_cells) == 200


# ---------------------------------------------------------------------------
# Test 2: resume logic — skip triples with 5/5 already done
# ---------------------------------------------------------------------------

def test_resume_skips_complete_triple(tmp_path: Path):
    """build_run_plan skips a (model, variant, domain) triple with 5 existing records."""
    from run_phase4b_variance import (
        N_RUNS_PER_CELL,
        VARIANCE_MODEL_IDS,
        build_run_plan,
    )

    # 3 triples are "complete" (5/5)
    completed_counts = {
        (VARIANCE_MODEL_IDS[0], "v1_s1", "family"): 5,
        (VARIANCE_MODEL_IDS[1], "v1_s2", "holidays"): 5,
        (VARIANCE_MODEL_IDS[2], "v2_soft1", "family"): 5,
    }

    plan = build_run_plan(VARIANCE_MODEL_IDS, completed_counts)

    # Total plan = 1800 - 3 complete triples × 5 runs = 1800 - 15 = 1785
    assert len(plan) == 1800 - (len(completed_counts) * N_RUNS_PER_CELL)

    # Verify none of the skipped triples appear
    for (mid, pv, domain) in completed_counts:
        assert not any(
            c.model_id == mid and c.prompt_version == pv and c.domain == domain
            for c in plan
        ), f"Triple ({mid}, {pv}, {domain}) should have been skipped"


def test_resume_partial_triple_runs_remaining(tmp_path: Path):
    """A triple with 3/5 records adds only 2 more run_indices to the plan."""
    from run_phase4b_variance import VARIANCE_MODEL_IDS, build_run_plan

    mid = VARIANCE_MODEL_IDS[0]
    completed_counts = {(mid, "v1_s1", "family"): 3}

    plan = build_run_plan(VARIANCE_MODEL_IDS, completed_counts)

    # The partial triple should contribute only 2 cells (run_idx 3, 4)
    partial_cells = sorted(
        [
            c for c in plan
            if c.model_id == mid and c.prompt_version == "v1_s1" and c.domain == "family"
        ],
        key=lambda c: c.run_index,
    )
    assert len(partial_cells) == 2
    assert [c.run_index for c in partial_cells] == [3, 4]


def test_count_completed_cells_informants(tmp_path: Path):
    """count_completed_cells counts records in informants.jsonl by (model, variant, domain)."""
    from run_phase4b_variance import count_completed_cells

    campaign_id = "phase4b-real-2026-05-08"
    campaign_marker = f"campaign_id={campaign_id}"

    inf_path = tmp_path / "informants.jsonl"
    fail_path = tmp_path / "failures.jsonl"

    # Write 3 records for triple A and 5 records for triple B
    model_a = "anthropic/claude-opus-4.6"
    model_b = "openai/gpt-5.4"

    lines = []
    for i in range(3):
        lines.append(_make_informant_jsonl_line(model_a, "v1_s1", "family", i, campaign_id))
    for i in range(5):
        lines.append(_make_informant_jsonl_line(model_b, "v1_s2", "holidays", i, campaign_id))
    # One record from a different campaign — must not be counted
    lines.append(_make_informant_jsonl_line(model_a, "v1_s1", "family", 9, "other-campaign"))

    inf_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    fail_path.write_text("", encoding="utf-8")

    counts = count_completed_cells(campaign_marker, inf_path, fail_path)

    assert counts.get((model_a, "v1_s1", "family"), 0) == 3
    assert counts.get((model_b, "v1_s2", "holidays"), 0) == 5
    # Other-campaign record must not be counted
    # The count for model_a triple should still be 3, not 4
    assert counts.get((model_a, "v1_s1", "family"), 0) == 3


def test_count_completed_cells_failures(tmp_path: Path):
    """count_completed_cells also counts records from failures.jsonl."""
    from run_phase4b_variance import count_completed_cells

    campaign_id = "phase4b-real-2026-05-08"
    campaign_marker = f"campaign_id={campaign_id}"

    inf_path = tmp_path / "informants.jsonl"
    fail_path = tmp_path / "failures.jsonl"

    model_a = "anthropic/claude-opus-4.6"

    # 2 successful informants
    inf_lines = [
        _make_informant_jsonl_line(model_a, "v1_s1", "family", 0, campaign_id),
        _make_informant_jsonl_line(model_a, "v1_s1", "family", 1, campaign_id),
    ]
    inf_path.write_text("\n".join(inf_lines) + "\n", encoding="utf-8")

    # 3 failures
    fail_lines = [
        _make_failure_jsonl_line(model_a, "v1_s1", "family", 2, campaign_id),
        _make_failure_jsonl_line(model_a, "v1_s1", "family", 3, campaign_id),
        _make_failure_jsonl_line(model_a, "v1_s1", "family", 4, campaign_id),
    ]
    fail_path.write_text("\n".join(fail_lines) + "\n", encoding="utf-8")

    counts = count_completed_cells(campaign_marker, inf_path, fail_path)

    # 2 informants + 3 failures = 5 attempts for the triple → skip
    assert counts.get((model_a, "v1_s1", "family"), 0) == 5


def test_resume_skips_triple_saturated_by_failures(tmp_path: Path):
    """build_run_plan skips a triple that has 5 entries in failures (all failed)."""
    from run_phase4b_variance import N_RUNS_PER_CELL, VARIANCE_MODEL_IDS, build_run_plan

    mid = VARIANCE_MODEL_IDS[0]
    # 5 failures = 5 "attempts" in the count → triple is considered done
    completed_counts = {(mid, "v1_s1", "family"): N_RUNS_PER_CELL}
    plan = build_run_plan(VARIANCE_MODEL_IDS, completed_counts)

    triple_cells = [
        c for c in plan
        if c.model_id == mid and c.prompt_version == "v1_s1" and c.domain == "family"
    ]
    assert len(triple_cells) == 0, "Triple saturated by failures should be skipped"


# ---------------------------------------------------------------------------
# Test 3: preflight-skip logic
# ---------------------------------------------------------------------------

def test_preflight_excludes_all_models_of_quota_exhausted_provider():
    """run_preflight drops ALL models on a provider that returns quota-exhausted."""
    from run_phase4b_variance import VARIANCE_MODEL_IDS, run_preflight

    # Patch _check_provider_available to return False for anthropic_api
    def _mock_check(collection_method: str, model_id: str) -> bool:
        return collection_method != "anthropic_api"

    with patch("run_phase4b_variance._check_provider_available", side_effect=_mock_check):
        active, skipped = run_preflight(VARIANCE_MODEL_IDS, dry_run=False)

    # All anthropic models should be in skipped
    anthropic_models = {
        mid for mid in VARIANCE_MODEL_IDS
        if MODEL_REGISTRY_FIXTURE.get(mid, {}).get("collection_method") == "anthropic_api"
    }
    skipped_flat = set()
    for mids in skipped.values():
        skipped_flat.update(mids)

    for amid in anthropic_models:
        assert amid in skipped_flat, f"{amid} should have been skipped"

    # Non-anthropic models should be active
    for mid in active:
        ref = _get_mock_registry().get(mid)
        if ref:
            assert ref.collection_method != "anthropic_api"


def _get_mock_registry() -> dict:
    """Return MODEL_REGISTRY if loaded."""
    try:
        from run_phase4b_variance import MODEL_REGISTRY as MR  # noqa: N811
        return MR  # type: ignore[return-value]
    except Exception:
        return {}


# Registry fixture for provider checks (maps model_id → {"collection_method": ...})
MODEL_REGISTRY_FIXTURE: dict[str, dict[str, str]] = {
    "anthropic/claude-opus-4.6": {"collection_method": "anthropic_api"},
    "anthropic/claude-sonnet-4.6": {"collection_method": "anthropic_api"},
    "anthropic/claude-opus-4.5": {"collection_method": "anthropic_api"},
    "openai/gpt-5.4": {"collection_method": "openai_api"},
    "openai/gpt-5.4-mini": {"collection_method": "openai_api"},
    "openai/gpt-5.2": {"collection_method": "openai_api"},
    "google/gemini-2.5-pro": {"collection_method": "google_ai"},
    "google/gemini-2.5-flash": {"collection_method": "google_ai"},
    "x-ai/grok-4.20": {"collection_method": "xai_api"},
    "x-ai/grok-4": {"collection_method": "xai_api"},
    "meta-llama/llama-4-maverick": {"collection_method": "openrouter"},
    "mistralai/mistral-small-2603": {"collection_method": "openrouter"},
    "qwen/qwen3.6-plus": {"collection_method": "openrouter"},
    "deepseek/deepseek-v3.2": {"collection_method": "openrouter"},
    "z-ai/glm-5.1": {"collection_method": "openrouter"},
    "microsoft/phi-4": {"collection_method": "openrouter"},
    "meta-llama/llama-4-scout": {"collection_method": "openrouter"},
    "mistralai/mistral-large-2512": {"collection_method": "openrouter"},
    "cohere/command-a": {"collection_method": "openrouter"},
    "google/gemma-4-26b-a4b-it": {"collection_method": "openrouter"},
}


def test_preflight_dry_run_returns_all_models():
    """run_preflight(dry_run=True) returns all models unchanged, no probes."""
    from run_phase4b_variance import VARIANCE_MODEL_IDS, run_preflight

    # dry_run=True must not call _check_provider_available at all
    with patch(
        "run_phase4b_variance._check_provider_available",
        side_effect=AssertionError("Should not call probe in dry_run mode"),
    ):
        active, skipped = run_preflight(VARIANCE_MODEL_IDS, dry_run=True)

    assert set(active) == set(VARIANCE_MODEL_IDS)
    assert skipped == {}


def test_preflight_all_providers_healthy():
    """When all providers are healthy, run_preflight returns all models active."""
    from run_phase4b_variance import VARIANCE_MODEL_IDS, run_preflight

    with patch(
        "run_phase4b_variance._check_provider_available",
        return_value=True,
    ):
        active, skipped = run_preflight(VARIANCE_MODEL_IDS, dry_run=False)

    assert set(active) == set(VARIANCE_MODEL_IDS)
    assert skipped == {}


def test_preflight_openai_quota_exhausted():
    """When openai_api returns quota-exhausted, all 3 OpenAI models are dropped."""
    from run_phase4b_variance import VARIANCE_MODEL_IDS, run_preflight

    def _mock_check(collection_method: str, model_id: str) -> bool:
        return collection_method != "openai_api"

    with patch("run_phase4b_variance._check_provider_available", side_effect=_mock_check):
        active, skipped = run_preflight(VARIANCE_MODEL_IDS, dry_run=False)

    # openai_api models: gpt-5.4, gpt-5.4-mini, gpt-5.2
    expected_skipped = {"openai/gpt-5.4", "openai/gpt-5.4-mini", "openai/gpt-5.2"}
    skipped_flat = {mid for mids in skipped.values() for mid in mids}
    assert expected_skipped == skipped_flat

    for mid in active:
        assert mid not in expected_skipped


# ---------------------------------------------------------------------------
# Test 4: success-rate computation
# ---------------------------------------------------------------------------

def test_success_rate_all_pass(tmp_path: Path):
    """5/5 qa_passed=True records → success_rate=1.0."""
    from run_phase4b_variance import compute_success_rates

    campaign_id = "phase4b-real-2026-05-08"
    model_id = "anthropic/claude-opus-4.6"
    pv = "v1_s1"
    domain = "family"

    inf_path = tmp_path / "informants.jsonl"
    fail_path = tmp_path / "failures.jsonl"

    lines = [
        _make_informant_jsonl_line(model_id, pv, domain, i, campaign_id, qa_passed=True)
        for i in range(5)
    ]
    inf_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    fail_path.write_text("", encoding="utf-8")

    rates = compute_success_rates(
        campaign_id,
        [model_id],
        [pv],
        [domain],
        inf_path,
        fail_path,
        n_attempts_targeted=5,
    )
    key = (model_id, pv, domain)
    assert key in rates
    assert rates[key]["passed"] == 5
    assert rates[key]["failed"] == 0
    assert rates[key]["success_rate"] == 1.0


def test_success_rate_all_failed(tmp_path: Path):
    """5/5 in failures.jsonl → success_rate=0.0."""
    from run_phase4b_variance import compute_success_rates

    campaign_id = "phase4b-real-2026-05-08"
    model_id = "openai/gpt-5.4"
    pv = "v1_s2"
    domain = "holidays"

    inf_path = tmp_path / "informants.jsonl"
    fail_path = tmp_path / "failures.jsonl"

    inf_path.write_text("", encoding="utf-8")
    fail_lines = [
        _make_failure_jsonl_line(model_id, pv, domain, i, campaign_id)
        for i in range(5)
    ]
    fail_path.write_text("\n".join(fail_lines) + "\n", encoding="utf-8")

    rates = compute_success_rates(
        campaign_id,
        [model_id],
        [pv],
        [domain],
        inf_path,
        fail_path,
        n_attempts_targeted=5,
    )
    key = (model_id, pv, domain)
    assert key in rates
    assert rates[key]["passed"] == 0
    assert rates[key]["failed"] == 5
    assert rates[key]["success_rate"] == 0.0


def test_success_rate_mixed(tmp_path: Path):
    """3 passed + 2 failed → success_rate = 3/5 = 0.6."""
    from run_phase4b_variance import compute_success_rates

    campaign_id = "phase4b-real-2026-05-08"
    model_id = "meta-llama/llama-4-maverick"
    pv = "v1_s3"
    domain = "family"

    inf_path = tmp_path / "informants.jsonl"
    fail_path = tmp_path / "failures.jsonl"

    inf_lines = [
        _make_informant_jsonl_line(model_id, pv, domain, i, campaign_id, qa_passed=True)
        for i in range(3)
    ]
    fail_lines = [
        _make_failure_jsonl_line(model_id, pv, domain, i + 3, campaign_id)
        for i in range(2)
    ]
    inf_path.write_text("\n".join(inf_lines) + "\n", encoding="utf-8")
    fail_path.write_text("\n".join(fail_lines) + "\n", encoding="utf-8")

    rates = compute_success_rates(
        campaign_id,
        [model_id],
        [pv],
        [domain],
        inf_path,
        fail_path,
        n_attempts_targeted=5,
    )
    key = (model_id, pv, domain)
    assert key in rates
    assert rates[key]["passed"] == 3
    assert rates[key]["failed"] == 2
    assert abs(rates[key]["success_rate"] - 0.6) < 1e-9


def test_success_rate_qa_failed_informant_counted_as_failed(tmp_path: Path):
    """An InformantRecord with qa_passed=False counts as failed, not successful."""
    from run_phase4b_variance import compute_success_rates

    campaign_id = "phase4b-real-2026-05-08"
    model_id = "z-ai/glm-5.1"
    pv = "v1_s4"
    domain = "holidays"

    inf_path = tmp_path / "informants.jsonl"
    fail_path = tmp_path / "failures.jsonl"

    # 4 qa_passed=True + 1 qa_passed=False
    inf_lines = [
        _make_informant_jsonl_line(model_id, pv, domain, i, campaign_id, qa_passed=(i < 4))
        for i in range(5)
    ]
    inf_path.write_text("\n".join(inf_lines) + "\n", encoding="utf-8")
    fail_path.write_text("", encoding="utf-8")

    rates = compute_success_rates(
        campaign_id,
        [model_id],
        [pv],
        [domain],
        inf_path,
        fail_path,
        n_attempts_targeted=5,
    )
    key = (model_id, pv, domain)
    assert key in rates
    assert rates[key]["passed"] == 4
    assert rates[key]["failed"] == 1
    # success_rate = 4/5 = 0.8
    assert abs(rates[key]["success_rate"] - 0.8) < 1e-9


def test_success_rate_excludes_other_campaigns(tmp_path: Path):
    """Records from a different campaign are not counted toward the target campaign."""
    from run_phase4b_variance import compute_success_rates

    campaign_id = "phase4b-real-2026-05-08"
    other_campaign = "phase4b-real-2026-04-30"
    model_id = "anthropic/claude-sonnet-4.6"
    pv = "v1_s5"
    domain = "family"

    inf_path = tmp_path / "informants.jsonl"
    fail_path = tmp_path / "failures.jsonl"

    # 2 records from the target campaign, 3 from another
    inf_lines = [
        _make_informant_jsonl_line(model_id, pv, domain, i, campaign_id)
        for i in range(2)
    ] + [
        _make_informant_jsonl_line(model_id, pv, domain, i + 10, other_campaign)
        for i in range(3)
    ]
    inf_path.write_text("\n".join(inf_lines) + "\n", encoding="utf-8")
    fail_path.write_text("", encoding="utf-8")

    rates = compute_success_rates(
        campaign_id,
        [model_id],
        [pv],
        [domain],
        inf_path,
        fail_path,
        n_attempts_targeted=5,
    )
    key = (model_id, pv, domain)
    # Only the 2 target-campaign records should be counted
    assert rates[key]["passed"] == 2
    assert rates[key]["success_rate"] == 2 / 5


def test_success_rate_empty_corpus(tmp_path: Path):
    """An empty corpus returns success_rate=0.0 for every requested triple."""
    from run_phase4b_variance import VARIANCE_MODEL_IDS, compute_success_rates

    campaign_id = "phase4b-real-2026-05-08"
    inf_path = tmp_path / "informants.jsonl"
    fail_path = tmp_path / "failures.jsonl"
    inf_path.write_text("", encoding="utf-8")
    fail_path.write_text("", encoding="utf-8")

    rates = compute_success_rates(
        campaign_id,
        [VARIANCE_MODEL_IDS[0]],
        ["v1_s1"],
        ["family"],
        inf_path,
        fail_path,
        n_attempts_targeted=5,
    )
    key = (VARIANCE_MODEL_IDS[0], "v1_s1", "family")
    assert rates[key]["success_rate"] == 0.0
    assert rates[key]["passed"] == 0
    assert rates[key]["failed"] == 0


# ---------------------------------------------------------------------------
# Test 5: cost estimation helper
# ---------------------------------------------------------------------------

def test_estimate_cell_cost_usd_known_model():
    """Cost estimate uses registry pricing correctly."""
    from run_phase4b_variance import estimate_cell_cost_usd

    registry_map = {
        "anthropic/claude-opus-4.6": {
            "pricing_input_per_m": 5.0,
            "pricing_output_per_m": 25.0,
        }
    }
    # 1000 input tokens, 500 output tokens
    # cost = (1000/1e6)*5.0 + (500/1e6)*25.0 = 0.005 + 0.0125 = 0.0175
    cost = estimate_cell_cost_usd("anthropic/claude-opus-4.6", registry_map, 1000, 500)
    assert abs(cost - 0.0175) < 1e-9


def test_estimate_cell_cost_usd_missing_model():
    """Missing model returns 0.0 without raising."""
    from run_phase4b_variance import estimate_cell_cost_usd

    cost = estimate_cell_cost_usd("unknown/model", {}, 1000, 500)
    assert cost == 0.0


# ---------------------------------------------------------------------------
# Test 6: module-level constants sanity checks
# ---------------------------------------------------------------------------

def test_20_model_ids():
    """VARIANCE_MODEL_IDS contains exactly 20 unique model_ids."""
    from run_phase4b_variance import VARIANCE_MODEL_IDS

    assert len(VARIANCE_MODEL_IDS) == 20
    assert len(set(VARIANCE_MODEL_IDS)) == 20


def test_9_prompt_versions():
    """VARIANCE_PROMPT_VERSIONS contains exactly 9 unique versions."""
    from run_phase4b_variance import VARIANCE_PROMPT_VERSIONS

    assert len(VARIANCE_PROMPT_VERSIONS) == 9
    assert len(set(VARIANCE_PROMPT_VERSIONS)) == 9
    # 8 v1_s* + 1 v2_soft1
    v1_s_versions = [pv for pv in VARIANCE_PROMPT_VERSIONS if pv.startswith("v1_s")]
    assert len(v1_s_versions) == 8
    assert "v2_soft1" in VARIANCE_PROMPT_VERSIONS


def test_2_domains():
    """VARIANCE_DOMAINS contains exactly 2 domains."""
    from run_phase4b_variance import VARIANCE_DOMAINS

    assert len(VARIANCE_DOMAINS) == 2
    assert "family" in VARIANCE_DOMAINS
    assert "holidays" in VARIANCE_DOMAINS


def test_n_runs_per_cell_is_5():
    """N_RUNS_PER_CELL is 5 as specified in plan §8 T4."""
    from run_phase4b_variance import N_RUNS_PER_CELL

    assert N_RUNS_PER_CELL == 5
