"""Tests for the two-pass re-QA logic in pipeline.load_records (T5).

CDA SME 2026-07-10 N5: corpus inclusion determined by recomputing QA against
the current scripts.qa_check rules (records-as-data, rules-as-code). Persisted
qa_passed is an audit artifact, not the authoritative filter.

Uses tests/fixtures/reasoning_class/informants.jsonl (7 records):
  r01: family, non-reasoning, qa_passed=True, recomputed=True
  r02: family, reasoning batch-A shape, qa_passed=False, recomputed=True (T1+T2 recal)
  r03: family, reasoning 700k latency, qa_passed=False, recomputed=False
  r04: family, reasoning visible=0, qa_passed=False, recomputed=True
  r05: family, 5 items (< MIN_FREELIST=10), qa_passed=True, recomputed=False
  r06: test_nonreasoning, non-reasoning, qa_passed=True, recomputed=True
  r07: test_allreasoning, reasoning, qa_passed=False, recomputed=True

No real API calls.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pytest
from cdb_analyze.pipeline import load_records

_FIXTURE_JSONL = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "reasoning_class"
    / "informants.jsonl"
)


def test_fixture_file_exists():
    assert _FIXTURE_JSONL.exists(), f"Missing fixture: {_FIXTURE_JSONL}"


def test_qa_only_false_returns_all_domain_records():
    """qa_only=False returns all records for the domain regardless of QA state."""
    records = load_records(_FIXTURE_JSONL, "family", qa_only=False)
    # Records 1-5, 8-9 are in the family domain (7 total after T8 dense fixtures added).
    assert len(records) == 7


def test_qa_only_false_domain_filter():
    """qa_only=False still filters by domain_slug."""
    records = load_records(_FIXTURE_JSONL, "test_nonreasoning", qa_only=False)
    assert len(records) == 1
    records_all = load_records(_FIXTURE_JSONL, "nonexistent_domain", qa_only=False)
    assert len(records_all) == 0


def test_recompute_includes_reasoning_record_batch_a_shape():
    """Record r02 (reasoning, batch-A shape) is included after T1+T2 recalibration.

    Persisted qa_passed=False because old Check 5 and Check 6 fired.
    After T1: latency 257000 < reasoning ceiling 600000 -> PASS.
    After T2: visible_tokens=40 vs expected=40 -> PASS.
    T5 recomputed=True -> included.
    """
    records = load_records(_FIXTURE_JSONL, "family", qa_only=True)
    ids = {r.informant_id for r in records}
    assert "rc-fix-r02-reasoning-batchA" in ids


def test_recompute_includes_reasoning_record_visible_zero():
    """Record r04 (reasoning, visible_tokens=0) is included.

    Check 6 is skipped when visible_tokens <= 0. Check 5 passes under
    the reasoning ceiling. Persisted qa_passed=False, recomputed=True.
    """
    records = load_records(_FIXTURE_JSONL, "family", qa_only=True)
    ids = {r.informant_id for r in records}
    assert "rc-fix-r04-reasoning-eq-tokens" in ids


def test_recompute_excludes_reasoning_record_still_failing():
    """Record r03 (reasoning, latency 700k ms) remains excluded.

    700000 ms exceeds the reasoning ceiling (600000 ms). Recomputed=False.
    """
    records = load_records(_FIXTURE_JSONL, "family", qa_only=True)
    ids = {r.informant_id for r in records}
    assert "rc-fix-r03-reasoning-700k" not in ids


def test_recompute_excludes_persisted_true_now_false():
    """Record r05 (5 items, qa_passed=True) is excluded after re-QA.

    Check 1 fires (5 < MIN_FREELIST_ITEMS=10). Persisted-True-now-False.
    """
    records = load_records(_FIXTURE_JSONL, "family", qa_only=True)
    ids = {r.informant_id for r in records}
    assert "rc-fix-r05-borderline" not in ids


def test_recompute_passes_non_reasoning_record():
    """Record r01 (non-reasoning, all checks pass) is included with qa_only=True."""
    records = load_records(_FIXTURE_JSONL, "family", qa_only=True)
    ids = {r.informant_id for r in records}
    assert "rc-fix-r01-nonreason" in ids


def test_qa_only_true_family_domain_count():
    """Family domain with qa_only=True returns exactly 5 records.

    r01 (non-reasoning PASS), r02 (reasoning PASS), r04 (reasoning PASS),
    r08 (dense-sonnet5 PASS via N9), r09 (dense+reasoning PASS via N2+N9).
    r03 (reasoning 700k latency FAIL), r05 (5 items FAIL) remain excluded.
    """
    records = load_records(_FIXTURE_JSONL, "family", qa_only=True)
    assert len(records) == 5


def test_recompute_includes_dense_tokenizer_record():
    """Record r08 (claude-sonnet-5, output=91 for 160-char rv) is included via N9.

    Old Check 6: 91 vs expected=40 (chars/4) -> ratio=1.275 -> FAIL.
    New Check 6 N9: 91 vs expected=91.43 (chars/1.75) -> ratio=0.005 -> PASS.
    Persisted qa_passed=False; recomputed=True.
    """
    records = load_records(_FIXTURE_JSONL, "family", qa_only=True)
    ids = {r.informant_id for r in records}
    assert "rc-fix-r08-dense-sonnet5" in ids


def test_recompute_includes_dense_and_reasoning_record():
    """Record r09 (claude-sonnet-5 + reasoning) is included via N2+N9 composition.

    visible_tokens = 5091-5000 = 91, expected_dense = 160/1.75 = 91.43, ratio=0.005 -> PASS.
    Persisted qa_passed=False; recomputed=True.
    """
    records = load_records(_FIXTURE_JSONL, "family", qa_only=True)
    ids = {r.informant_id for r in records}
    assert "rc-fix-r09-dense-and-reasoning" in ids


def test_divergence_logged_both_directions(caplog: pytest.LogCaptureFixture):
    """Divergence in both directions is logged at INFO with correct counts.

    Family domain (7 total records):
    - persisted-True-now-False: r05 (5 items, qa_passed=True, recomputed=False) -> count=1
    - persisted-False-now-True: r02, r04, r08, r09 (qa_passed=False, recomputed=True) -> count=4
    """
    with caplog.at_level(logging.INFO, logger="cdb_analyze.pipeline"):
        load_records(_FIXTURE_JSONL, "family", qa_only=True)

    log_text = " ".join(caplog.messages)
    assert "persisted-True-now-False: 1" in log_text
    assert "persisted-False-now-True: 4" in log_text
