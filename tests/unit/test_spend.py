"""Tests for spend cap enforcement. See ARCHITECTURE.md §6.2."""

import json
import tempfile
from pathlib import Path

from cdb_collect.spend import check_spend, compute_cost, get_monthly_spend


def test_check_spend_ok():
    assert check_spend(100.0, cap_usd=300.0) == "ok"
    assert check_spend(0.0, cap_usd=300.0) == "ok"
    assert check_spend(239.99, cap_usd=300.0) == "ok"


def test_check_spend_warning():
    assert check_spend(240.0, cap_usd=300.0) == "warning"
    assert check_spend(280.0, cap_usd=300.0) == "warning"
    assert check_spend(299.99, cap_usd=300.0) == "warning"


def test_check_spend_halt():
    assert check_spend(300.0, cap_usd=300.0) == "halt"
    assert check_spend(350.0, cap_usd=300.0) == "halt"


def test_check_spend_zero_cap():
    assert check_spend(0.0, cap_usd=0.0) == "halt"


def test_compute_cost_known_model():
    # claude-opus-4-6: $15/M input, $75/M output
    cost = compute_cost(1_000_000, 0, "claude-opus-4-6")
    assert abs(cost - 15.0) < 0.01

    cost = compute_cost(0, 1_000_000, "claude-opus-4-6")
    assert abs(cost - 75.0) < 0.01


def test_compute_cost_unknown_model():
    # Falls back to default pricing
    cost = compute_cost(1_000_000, 0, "unknown-model-xyz")
    assert cost > 0.0


def test_get_monthly_spend_empty():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        path = Path(f.name)

    assert get_monthly_spend(path, "2026-04") == 0.0
    path.unlink()


def test_get_monthly_spend_nonexistent():
    path = Path("/tmp/nonexistent_spend_test.jsonl")
    assert get_monthly_spend(path, "2026-04") == 0.0


def test_get_monthly_spend_with_records():
    records = [
        {
            "collection_date": "2026-04-13T10:00:00",
            "model_id": "claude-opus-4-6",
            "freelist": {"input_tokens": 100, "output_tokens": 200},
            "pile_sort": {"input_tokens": 0, "output_tokens": 0},
            "interview": {"input_tokens": 0, "output_tokens": 0},
        },
        {
            "collection_date": "2026-03-15T10:00:00",
            "model_id": "claude-opus-4-6",
            "freelist": {"input_tokens": 500, "output_tokens": 500},
            "pile_sort": {"input_tokens": 0, "output_tokens": 0},
            "interview": {"input_tokens": 0, "output_tokens": 0},
        },
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
        path = Path(f.name)

    spend_april = get_monthly_spend(path, "2026-04")
    spend_march = get_monthly_spend(path, "2026-03")

    assert spend_april > 0.0
    assert spend_march > 0.0
    assert spend_april != spend_march  # Different token counts

    path.unlink()
