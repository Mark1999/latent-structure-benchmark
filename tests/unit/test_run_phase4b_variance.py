"""Unit tests for scripts/run_phase4b_variance.py.

Tests cover:
1. Run-plan generator: 20 × 9 × 5 × 2 = 1,800 cells with correct field combinations.
2. Resume logic: a triple with 5/5 existing records is skipped.
3. Preflight-skip logic: models on a quota-exhausted provider are dropped from the plan.
4. Success-rate computation against a small fixture corpus.
5. Module-level constants sanity checks.
6. run_cell retry budget: first-fail-second-pass appends 1 informant row.
7. run_cell retry budget: both-fail appends 1 failure row.
8. append_success_rates_to_log: pre-existing rows preserved; new rows inserted after
   the pending placeholder.

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
# Tests for _exc_chain_str and _is_quota_exhausted helpers (unit-level)
# ---------------------------------------------------------------------------

def test_exc_chain_str_single_exception():
    """_exc_chain_str on a plain exception returns its str, lowercased."""
    from run_phase4b_variance import _exc_chain_str

    exc = ValueError("Something went wrong")
    result = _exc_chain_str(exc)
    assert "something went wrong" in result


def test_exc_chain_str_chained_exception():
    """_exc_chain_str includes messages from __cause__ in the chain."""
    from run_phase4b_variance import _exc_chain_str

    try:
        inner = RuntimeError("HTTP 429: insufficient_quota")
        raise RuntimeError("openai api call failed after 5 retries") from inner
    except Exception as exc:
        result = _exc_chain_str(exc)

    # The outer message
    assert "failed after 5 retries" in result
    # The inner (cause) message — this is the key: str(exc) alone would miss this
    assert "429" in result
    assert "insufficient_quota" in result


def test_is_quota_exhausted_detects_direct_429():
    """_is_quota_exhausted returns True for a plain '429' exception."""
    from run_phase4b_variance import _is_quota_exhausted

    exc = Exception("HTTP 429: rate_limit_exceeded")
    assert _is_quota_exhausted(exc) is True


def test_is_quota_exhausted_detects_chained_429():
    """_is_quota_exhausted returns True when 429 is only in the __cause__."""
    from run_phase4b_variance import _is_quota_exhausted

    # Simulate the real adapter chain:
    # PartialSessionError(str(RuntimeError(...))) wraps RuntimeError from _RetryableError
    inner = Exception('HTTP 429: {"error":{"type":"insufficient_quota"}}')
    middle = RuntimeError("openai api call failed after 5 retries")
    middle.__cause__ = inner
    outer = Exception(str(middle))
    outer.__cause__ = middle

    # str(outer) = "openai api call failed after 5 retries" — no 429 marker
    assert "429" not in str(outer).lower()
    # But _is_quota_exhausted must still detect it via the chain
    assert _is_quota_exhausted(outer) is True


def test_is_quota_exhausted_returns_false_for_unrelated_error():
    """_is_quota_exhausted returns False for a parse error with no quota signal."""
    from run_phase4b_variance import _is_quota_exhausted

    exc = ValueError("JSON parse error: unexpected token at position 42")
    assert _is_quota_exhausted(exc) is False


def test_is_quota_exhausted_returns_false_for_network_timeout():
    """_is_quota_exhausted returns False for a timeout error."""
    from run_phase4b_variance import _is_quota_exhausted

    exc = TimeoutError("Connection timed out after 600s")
    assert _is_quota_exhausted(exc) is False


# ---------------------------------------------------------------------------
# Test: _check_provider_available detects real adapter return shape on 429
# ---------------------------------------------------------------------------

def test_check_provider_available_detects_chained_429_error():
    """The adapter exhausts its retry budget on persistent 429 and raises a
    chained exception: PartialSessionError -> RuntimeError -> _RetryableError
    ("HTTP 429: ...").  _check_provider_available must detect the quota signal
    in the chain and return False (not True).

    This is the bug that was discovered 2026-05-08: the preflight wrapper
    only checked str(exc), which returned the outer RuntimeError message
    "openai api call failed after 5 retries" — containing no 429 marker —
    so the provider was logged as healthy despite exhausting its retry
    budget on every probe attempt.
    """
    from run_phase4b_variance import _check_provider_available

    # Reproduce the real exception chain from openai_compat._complete_with_retry
    # → runner.run_informant when HTTP 429 is returned on every attempt.
    #
    # openai_compat._RetryableError("HTTP 429: {\"error\":{\"type\":\"insufficient_quota\"}}")
    retryable = RuntimeError(
        'HTTP 429: {"error":{"message":"You exceeded your current quota",'
        '"type":"insufficient_quota","code":"insufficient_quota"}}'
    )
    # RuntimeError raised after _MAX_RETRIES exhausted, chained from _RetryableError
    retry_exhausted = RuntimeError("openai API call failed after 5 retries")
    retry_exhausted.__cause__ = retryable

    # runner.run_informant wraps in PartialSessionError whose str() = str(cause)
    # = "openai API call failed after 5 retries" (no 429 marker in top-level str)
    partial_session_exc = Exception("openai API call failed after 5 retries")
    partial_session_exc.__cause__ = retry_exhausted

    # asyncio.run(run_informant(...)) raises this PartialSessionError-shaped exception.
    # Patch at the asyncio.run level so no real async infrastructure is needed.
    def _fake_asyncio_run(coro):
        coro.close()  # prevent ResourceWarning
        raise partial_session_exc

    # Minimal ModelRef-like fixture
    class _FakeRef:
        model_id = "openai/gpt-5.4"
        collection_method = "openai_api"
        family = "gpt"
        provider = "openai"
        open_weights = False
        origin = "us"

    with (
        patch("run_phase4b_variance.MODEL_REGISTRY", {"openai/gpt-5.4": _FakeRef()}),
        patch("run_phase4b_variance._create_adapter", return_value=object()),
        patch("run_phase4b_variance.asyncio.run", side_effect=_fake_asyncio_run),
        patch("run_phase4b_variance.load_domain", return_value=object()),
    ):
        result = _check_provider_available("openai_api", "openai/gpt-5.4")

    # Must return False (quota-exhausted detected), not True (healthy)
    assert result is False, (
        "_check_provider_available returned True for a chained 429/insufficient_quota "
        "exception — the preflight bug has not been fixed"
    )


def test_check_provider_available_returns_true_for_transient_parse_error():
    """A parse error (not a quota signal) should NOT cause preflight to skip
    the provider.  Transient errors are surfaced per-cell during the campaign."""
    from run_phase4b_variance import _check_provider_available

    parse_error = ValueError("JSON parse error: unexpected token at position 42")

    def _fake_asyncio_run(coro):
        coro.close()
        raise parse_error

    class _FakeRef:
        model_id = "openai/gpt-5.4"
        collection_method = "openai_api"
        family = "gpt"
        provider = "openai"
        open_weights = False
        origin = "us"

    with (
        patch("run_phase4b_variance.MODEL_REGISTRY", {"openai/gpt-5.4": _FakeRef()}),
        patch("run_phase4b_variance._create_adapter", return_value=object()),
        patch("run_phase4b_variance.asyncio.run", side_effect=_fake_asyncio_run),
        patch("run_phase4b_variance.load_domain", return_value=object()),
    ):
        result = _check_provider_available("openai_api", "openai/gpt-5.4")

    # Parse error is transient — provider is considered available
    assert result is True, (
        "_check_provider_available returned False for a transient parse error; "
        "only quota/429 signals should mark a provider as unavailable"
    )


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
# Test 5: module-level constants sanity checks
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


# ---------------------------------------------------------------------------
# Test 6: run_cell retry budget (MAX_ATTEMPTS_PER_CELL = 2)
# ---------------------------------------------------------------------------
#
# run_cell() calls asyncio.run(_run_one_informant(...)) internally.
# We mock _run_one_informant at the module level so no provider adapter is
# instantiated.  append_record / append_failure are also mocked to capture
# what would have been written to disk.
#
# Scenario A: attempt 1 raises ValueError, attempt 2 succeeds.
#   Expected: append_record called once, append_failure not called, return "PASS".
#
# Scenario B: both attempts raise ValueError.
#   Expected: append_record not called, append_failure called once, return "FAILED".

def _make_mock_record(model_id: str = "anthropic/claude-opus-4.6") -> object:
    """Return a minimal object that satisfies run_cell's attribute access."""

    class _Rec:
        input_tokens = 100
        output_tokens = 50

    return _Rec()


def _make_cell(
    model_id: str = "anthropic/claude-opus-4.6",
    prompt_version: str = "v1_s1",
    domain: str = "family",
    run_index: int = 0,
) -> object:
    from run_phase4b_variance import VarianceCell
    return VarianceCell(model_id, prompt_version, domain, run_index)


def test_run_cell_retry_first_fail_second_pass(tmp_path: Path):
    """run_cell attempt-1 fails, attempt-2 passes → PASS returned, 1 informant appended."""
    import io
    from unittest.mock import patch

    from run_phase4b_variance import CampaignStats, run_cell

    cell = _make_cell()
    stats = CampaignStats()
    log_fh = io.StringIO()
    informants_path = tmp_path / "informants.jsonl"
    failures_path = tmp_path / "failures.jsonl"

    mock_record = _make_mock_record()

    call_count = {"n": 0}

    async def _fail_then_pass(*args, **kwargs):
        call_count["n"] += 1
        if call_count["n"] == 1:
            raise ValueError("Simulated transient failure on attempt 1")
        return mock_record

    with (
        patch("run_phase4b_variance._run_one_informant", side_effect=_fail_then_pass),
        patch("run_phase4b_variance.append_record") as mock_append_record,
        patch("run_phase4b_variance.append_failure") as mock_append_failure,
        patch("run_phase4b_variance.time.sleep"),  # skip retry delay
    ):
        result = run_cell(
            cell=cell,
            cell_index=1,
            total=10,
            campaign_id="phase4b-real-2026-05-08",
            informants_path=informants_path,
            failures_path=failures_path,
            stats=stats,
            log_fh=log_fh,
        )

    assert result == "PASS", f"Expected PASS, got {result!r}"
    assert call_count["n"] == 2, "Expected exactly 2 _run_one_informant calls"
    mock_append_record.assert_called_once_with(mock_record, informants_path)
    mock_append_failure.assert_not_called()
    assert stats.n_pass == 1
    assert stats.n_failed == 0


def test_run_cell_retry_both_fail(tmp_path: Path):
    """run_cell both attempts fail → FAILED returned, 1 failure row appended."""
    import io
    from unittest.mock import patch

    from run_phase4b_variance import CampaignStats, run_cell

    cell = _make_cell()
    stats = CampaignStats()
    log_fh = io.StringIO()
    informants_path = tmp_path / "informants.jsonl"
    failures_path = tmp_path / "failures.jsonl"

    async def _always_fail(*args, **kwargs):
        raise ValueError("Simulated persistent failure")

    with (
        patch("run_phase4b_variance._run_one_informant", side_effect=_always_fail),
        patch("run_phase4b_variance.append_record") as mock_append_record,
        patch("run_phase4b_variance.append_failure") as mock_append_failure,
        patch("run_phase4b_variance.time.sleep"),  # skip retry delay
    ):
        result = run_cell(
            cell=cell,
            cell_index=1,
            total=10,
            campaign_id="phase4b-real-2026-05-08",
            informants_path=informants_path,
            failures_path=failures_path,
            stats=stats,
            log_fh=log_fh,
        )

    assert result == "FAILED", f"Expected FAILED, got {result!r}"
    mock_append_record.assert_not_called()
    mock_append_failure.assert_called_once()
    # Confirm the failure context carries model_id and campaign_id
    call_kwargs = mock_append_failure.call_args
    # append_failure(last_exc, failure_context, failures_path, ...)
    failure_context = call_kwargs.args[1]
    assert failure_context["model_id"] == cell.model_id
    assert failure_context["campaign_id"] == "phase4b-real-2026-05-08"
    assert stats.n_failed == 1
    assert stats.n_pass == 0


# ---------------------------------------------------------------------------
# Test 7: append_success_rates_to_log — append-only invariant
# ---------------------------------------------------------------------------
#
# append_success_rates_to_log() reads the existing log and inserts new rows
# only at the "*(Phase 4b T4 — pending)*" placeholder line. Pre-existing rows
# must survive unchanged.

def test_append_success_rates_preserves_preexisting_rows(tmp_path: Path):
    """Pre-existing rows in PROMPT_EVOLUTION_LOG.md are unchanged after append."""
    from run_phase4b_variance import append_success_rates_to_log

    log_path = tmp_path / "PROMPT_EVOLUTION_LOG.md"

    # Minimal log with one pre-existing campaign row and the pending placeholder
    initial_content = """\
# LSB Prompt Evolution Log

### v1_s1 — paraphrase 1

#### Campaigns that consumed v1_s1

| campaign_id | model_id | domain | N | passed | failed | success_rate |
|---|---|---|---:|---:|---:|---:|
| phase4b-prior-2026-04-01 | anthropic/claude-opus-4.6 | family | 5 | 5 | 0 | 1.00 |
| *(Phase 4b T4 — pending)* | — | — | — | — | — | — |

---
"""
    log_path.write_text(initial_content, encoding="utf-8")

    # One new row for v1_s1
    rates = {
        ("anthropic/claude-opus-4.6", "v1_s1", "family"): {
            "passed": 4,
            "failed": 1,
            "n_attempts_targeted": 5,
            "success_rate": 0.8,
        }
    }
    append_success_rates_to_log("phase4b-real-2026-05-08", rates, log_path)

    result = log_path.read_text(encoding="utf-8")

    # Pre-existing row must still be present verbatim
    prior_row = (
        "| phase4b-prior-2026-04-01 | anthropic/claude-opus-4.6"
        " | family | 5 | 5 | 0 | 1.00 |"
    )
    assert prior_row in result
    # Placeholder line must still be present (append inserts after it, does not delete it)
    assert "*(Phase 4b T4 — pending)*" in result
    # New row must be present
    assert "phase4b-real-2026-05-08" in result
    assert "anthropic/claude-opus-4.6" in result


def test_append_success_rates_new_row_after_placeholder(tmp_path: Path):
    """New success-rate rows are inserted after the pending placeholder, not before."""
    from run_phase4b_variance import append_success_rates_to_log

    log_path = tmp_path / "PROMPT_EVOLUTION_LOG.md"

    initial_content = """\
### v1_s2

| campaign_id | model_id | domain | N | passed | failed | success_rate |
|---|---|---|---:|---:|---:|---:|
| *(Phase 4b T4 — pending)* | — | — | — | — | — | — |

---
"""
    log_path.write_text(initial_content, encoding="utf-8")

    rates = {
        ("openai/gpt-5.4", "v1_s2", "holidays"): {
            "passed": 5,
            "failed": 0,
            "n_attempts_targeted": 5,
            "success_rate": 1.0,
        }
    }
    append_success_rates_to_log("phase4b-real-2026-05-08", rates, log_path)

    result = log_path.read_text(encoding="utf-8")
    lines = result.splitlines()

    # Find index of placeholder line and new row line
    placeholder_idx = next(
        i for i, line in enumerate(lines) if "*(Phase 4b T4 — pending)*" in line
    )
    new_row_idx = next(
        i for i, line in enumerate(lines) if "phase4b-real-2026-05-08" in line
    )
    assert new_row_idx > placeholder_idx, (
        "New row should appear after the placeholder line, not before it"
    )
