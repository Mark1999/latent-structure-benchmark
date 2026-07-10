"""Tests for scripts/preflight_reasoning_class_representation.py (T4 + T8 N11).

T4 cases:
  1. domain with 0 reasoning + >0 non-reasoning -> exit 1
  2. domain with mixed (>0 reasoning + >0 non-reasoning) -> exit 0
  3. domain with only reasoning (non_reasoning == 0) -> exit 0 (SKIP)

T8 N11 cases:
  4. model with median chars/token < 2.5 triggers N11 warning (warning-only)
  5. model with median chars/token in [2.5, 3.0] does not trigger N11 warning

Uses tests/fixtures/reasoning_class/informants.jsonl.
No real API calls.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from scripts.preflight_reasoning_class_representation import (
    detect_dense_tokenizer_candidates,
    main,
)

_FIXTURE_JSONL = str(
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "reasoning_class"
    / "informants.jsonl"
)


def test_only_non_reasoning_exits_1():
    """Domain with 0 reasoning-class records and >0 non-reasoning records -> exit 1.

    'test_nonreasoning' domain has only record r06 (thoughts_token_count=0).
    After T5 re-QA: 1 non-reasoning, 0 reasoning -> FAIL -> exit 1.
    """
    result = main(["--domains", "test_nonreasoning", "--jsonl", _FIXTURE_JSONL])
    assert result == 1


def test_mixed_domain_exits_0():
    """Domain with both reasoning and non-reasoning records -> exit 0.

    'family' domain after T5+T8 re-QA:
    r01 (non-reasoning PASS), r02 (reasoning PASS), r04 (reasoning PASS),
    r08 (dense, non-reasoning PASS), r09 (dense+reasoning PASS).
    non_reasoning=2, reasoning=3 -> PASS -> exit 0.
    """
    result = main(["--domains", "family", "--jsonl", _FIXTURE_JSONL])
    assert result == 0


def test_all_reasoning_exits_0():
    """Domain with only reasoning-class records (no non-reasoning) -> exit 0 (SKIP).

    'test_allreasoning' domain after T5 re-QA:
    r07 (thoughts_token_count=5000, qa_passed=False, recomputed=True).
    non_reasoning=0, reasoning=1 -> SKIP -> exit 0.
    """
    result = main(["--domains", "test_allreasoning", "--jsonl", _FIXTURE_JSONL])
    assert result == 0


def test_multiple_domains_any_fail_exits_1():
    """Multiple domains: if any domain fails, exit 1."""
    result = main([
        "--domains", "family,test_nonreasoning",
        "--jsonl", _FIXTURE_JSONL,
    ])
    assert result == 1


def test_multiple_domains_all_pass_exits_0():
    """Multiple domains: if all pass (or SKIP), exit 0."""
    result = main([
        "--domains", "family,test_allreasoning",
        "--jsonl", _FIXTURE_JSONL,
    ])
    assert result == 0


# ── T8 N11: dense-tokenizer roster-maintenance detector ──────────────────────

_FIXTURE_JSONL_PATH = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "reasoning_class"
    / "informants.jsonl"
)


def test_n11_warning_for_model_below_lower_threshold():
    """Model with median chars/token < 2.5 appears in detect_dense_tokenizer_candidates.

    test_n11 domain: test/suspicious-dense-x has 2 records with:
    output=75 (cpt=160/75=2.13) and output=73 (cpt=160/73=2.19).
    median = 2.16 < 2.5 -> warning returned.
    """
    warnings = detect_dense_tokenizer_candidates(_FIXTURE_JSONL_PATH, ["test_n11"])
    warned_ids = {mid for mid, _ in warnings}
    assert "test/suspicious-dense-x" in warned_ids


def test_n11_no_warning_for_model_in_normal_range():
    """Model with median chars/token in [2.5, 3.0] does not trigger N11 warning.

    test_n11 domain: test/normal-tokenizer-y has 2 records with:
    output=54 (cpt=160/54=2.96) and output=56 (cpt=160/56=2.86).
    median = 2.91 -> in range [2.5, 3.0] -> no warning.
    """
    warnings = detect_dense_tokenizer_candidates(_FIXTURE_JSONL_PATH, ["test_n11"])
    warned_ids = {mid for mid, _ in warnings}
    assert "test/normal-tokenizer-y" not in warned_ids


def test_n11_dense_roster_models_not_detected():
    """Models in DENSE_TOKENIZER_MODEL_IDS are excluded from N11 detection.

    The N11 detector only applies to models NOT already in the roster.
    claude-sonnet-5 (in the roster) must not appear in warnings even if its
    chars/token would otherwise trigger the check.
    """
    # family domain has claude-sonnet-5 records that pass QA (r08, r09)
    warnings = detect_dense_tokenizer_candidates(_FIXTURE_JSONL_PATH, ["family"])
    warned_ids = {mid for mid, _ in warnings}
    assert "claude-sonnet-5" not in warned_ids


def test_n11_warning_does_not_affect_exit_code():
    """N11 warnings do not change exit code; only N6 failures do.

    test_n11 domain has a suspicious-dense model (N11 warning) but no
    reasoning-class vs non-reasoning-class imbalance -> exit 0.
    """
    result = main(["--domains", "test_n11", "--jsonl", _FIXTURE_JSONL])
    assert result == 0


# ─── Gap coverage: N11 threshold boundary semantics ──────────────────────────
# The N11 detector uses strict inequalities: warn when median < 2.5 OR > 3.0.
# At exactly 2.5 or 3.0, the model is within the pre-Claude-5 cluster and
# must NOT trigger a warning. The existing tests only cover median ~2.16 (below
# 2.5) and ~2.91 (clearly in range), leaving the exact boundary untested.
#
# Records are constructed via SimpleNamespace so no JSONL write or Pydantic
# parse is needed; detect_dense_tokenizer_candidates uses getattr() throughout.


def _boundary_record(
    model_id: str,
    rv_len: int,
    output_tokens: int,
    run_index: int = 0,
) -> object:
    """Minimal record object compatible with detect_dense_tokenizer_candidates."""
    fl = SimpleNamespace(response_verbatim="x" * rv_len, output_tokens=output_tokens)
    return SimpleNamespace(model_id=model_id, run_index=run_index, freelist=fl)


def test_n11_exactly_at_lower_threshold_not_warned():
    """Median chars/token = exactly 2.5 is NOT warned (condition is strictly < 2.5).

    Two records: rv_len=160, output_tokens=64 -> 160/64 = 2.5 exactly.
    Median of [2.5, 2.5] = 2.5. Since 2.5 < 2.5 is False and 2.5 > 3.0 is False,
    no warning is emitted.
    """
    records = [
        _boundary_record("test/at-lower-boundary", rv_len=160, output_tokens=64, run_index=0),
        _boundary_record("test/at-lower-boundary", rv_len=160, output_tokens=64, run_index=1),
    ]
    with patch(
        "scripts.preflight_reasoning_class_representation.load_records",
        return_value=records,
    ):
        warnings = detect_dense_tokenizer_candidates(Path("fake.jsonl"), ["test_boundary"])

    warned_ids = {mid for mid, _ in warnings}
    assert "test/at-lower-boundary" not in warned_ids


def test_n11_just_below_lower_threshold_is_warned():
    """Median chars/token just below 2.5 DOES trigger N11 warning.

    Two records: rv_len=160, output_tokens=65 -> 160/65 = 2.4615...
    Median = 2.4615 < 2.5 -> warning emitted.
    Confirms the strict-less-than semantics are active.
    """
    records = [
        _boundary_record("test/sub-lower-bound", rv_len=160, output_tokens=65, run_index=0),
        _boundary_record("test/sub-lower-bound", rv_len=160, output_tokens=65, run_index=1),
    ]
    with patch(
        "scripts.preflight_reasoning_class_representation.load_records",
        return_value=records,
    ):
        warnings = detect_dense_tokenizer_candidates(Path("fake.jsonl"), ["test_boundary"])

    warned_ids = {mid for mid, _ in warnings}
    assert "test/sub-lower-bound" in warned_ids


def test_n11_exactly_at_upper_threshold_not_warned():
    """Median chars/token = exactly 3.0 is NOT warned (condition is strictly > 3.0).

    Two records: rv_len=150, output_tokens=50 -> 150/50 = 3.0 exactly.
    Median of [3.0, 3.0] = 3.0. Since 3.0 > 3.0 is False, no warning is emitted.
    """
    records = [
        _boundary_record("test/at-upper-boundary", rv_len=150, output_tokens=50, run_index=0),
        _boundary_record("test/at-upper-boundary", rv_len=150, output_tokens=50, run_index=1),
    ]
    with patch(
        "scripts.preflight_reasoning_class_representation.load_records",
        return_value=records,
    ):
        warnings = detect_dense_tokenizer_candidates(Path("fake.jsonl"), ["test_boundary"])

    warned_ids = {mid for mid, _ in warnings}
    assert "test/at-upper-boundary" not in warned_ids


def test_n11_just_above_upper_threshold_is_warned():
    """Median chars/token just above 3.0 DOES trigger N11 warning.

    Two records: rv_len=151, output_tokens=50 -> 151/50 = 3.02.
    Median = 3.02 > 3.0 -> warning emitted.
    Confirms the strict-greater-than semantics are active.
    """
    records = [
        _boundary_record("test/above-upper-bound", rv_len=151, output_tokens=50, run_index=0),
        _boundary_record("test/above-upper-bound", rv_len=151, output_tokens=50, run_index=1),
    ]
    with patch(
        "scripts.preflight_reasoning_class_representation.load_records",
        return_value=records,
    ):
        warnings = detect_dense_tokenizer_candidates(Path("fake.jsonl"), ["test_boundary"])

    warned_ids = {mid for mid, _ in warnings}
    assert "test/above-upper-bound" in warned_ids
