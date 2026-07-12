"""Tests for the N15/N16 re-QA logic in pipeline.load_records (R1/R2).

CDA SME 2026-07-10 N5 / 2026-07-11 N15/N16:
  - Per-record checks (1/3/4/5/6/7/8) recompute from record fields alone.
  - Check 2 (reference-set-dependent) is disabled by passing [record] as the
    reference set; its len(same_runs) < 2 self-guard fires.
  - Persisted-False records include iff per-record pass AND no Check-2 signature
    in qa_notes (bare percentage matching f"{ratio:.1%}" runner.py format).
  - Persisted-True records include iff per-record pass; exclusion triggers N16
    monotonicity guard (RuntimeError).

Uses tests/fixtures/reasoning_class/informants.jsonl (17 records after R1/R2
fixture additions):

  Family domain (7 records):
    r01: family, non-reasoning, qa_passed=True  -> included (included-unchanged)
    r02: family, reasoning batch-A, qa_passed=False -> included (recover: N1+N2)
    r03: family, reasoning 700k latency, qa_passed=False -> excluded (still fails)
    r04: family, reasoning visible=0, qa_passed=False -> included (recover: N2)
    r08: family, dense-sonnet5, qa_passed=False -> included (recover: N9)
    r09: family, dense+reasoning, qa_passed=False -> included (recover: N2+N9)
    r15: family, check2-sig in qa_notes, qa_passed=False, per-record pass
         -> excluded (stay-excluded-on-%-signature)

  test_guard_1 domain (1 record):
    r05: test_guard_1, qa_passed=True, 5 items (Check 1 fails)
         -> N16 RuntimeError (excluded-feeding-guard, 1-model case)

  test_guard_2 domain (2 records):
    r17: test_guard_2, model test/borderline-e2, qa_passed=True, 5 items
    r18: test_guard_2, model test/borderline-f, qa_passed=True, 5 items
         -> N16 RuntimeError (excluded-feeding-guard, 2-model case)

No real API calls.
"""

from __future__ import annotations

import json
import logging
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from cdb_analyze.pipeline import _has_check2_signature, load_records

_FIXTURE_JSONL = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "reasoning_class"
    / "informants.jsonl"
)


def test_fixture_file_exists():
    assert _FIXTURE_JSONL.exists(), f"Missing fixture: {_FIXTURE_JSONL}"


# ─── qa_only=False passthrough ────────────────────────────────────────────────


def test_qa_only_false_returns_all_domain_records():
    """qa_only=False returns all records for the domain regardless of QA state."""
    records = load_records(_FIXTURE_JSONL, "family", qa_only=False)
    # Family domain: r01, r02, r03, r04, r08, r09, r15 = 7 records.
    # (r05 moved to test_guard_1 in R1 fixture update.)
    assert len(records) == 7


def test_qa_only_false_domain_filter():
    """qa_only=False still filters by domain_slug."""
    records = load_records(_FIXTURE_JSONL, "test_nonreasoning", qa_only=False)
    assert len(records) == 1
    records_all = load_records(_FIXTURE_JSONL, "nonexistent_domain", qa_only=False)
    assert len(records_all) == 0


# ─── R1: four fixture cases ───────────────────────────────────────────────────


def test_r1_recover_reasoning_record_batch_a_shape():
    """R1 recover: r02 (reasoning, batch-A shape) is included.

    Persisted qa_passed=False (old Check 5+6 fired). After T1+T2 recalibration:
    latency 257000 < reasoning ceiling 600000 (N1) and visible=40 vs expected=40 (N2).
    Per-record pass + no Check-2 sig -> included.
    """
    records = load_records(_FIXTURE_JSONL, "family", qa_only=True)
    ids = {r.informant_id for r in records}
    assert "rc-fix-r02-reasoning-batchA" in ids


def test_r1_recover_reasoning_record_visible_zero():
    """R1 recover: r04 (reasoning, visible_tokens=0) is included.

    Check 6 is skipped when visible_tokens <= 0. Check 5 passes under the
    reasoning ceiling. Persisted qa_passed=False; per-record pass -> included.
    """
    records = load_records(_FIXTURE_JSONL, "family", qa_only=True)
    ids = {r.informant_id for r in records}
    assert "rc-fix-r04-reasoning-eq-tokens" in ids


def test_r1_recover_dense_tokenizer_record():
    """R1 recover: r08 (claude-sonnet-5, dense N9) is included.

    Old Check 6: 91 vs expected=40 (chars/4) -> ratio=1.275 -> FAIL.
    New Check 6 N9: 91 vs expected=91.43 (chars/1.75) -> ratio=0.005 -> PASS.
    Persisted qa_passed=False; per-record pass + no sig -> included.
    """
    records = load_records(_FIXTURE_JSONL, "family", qa_only=True)
    ids = {r.informant_id for r in records}
    assert "rc-fix-r08-dense-sonnet5" in ids


def test_r1_recover_dense_and_reasoning_record():
    """R1 recover: r09 (claude-sonnet-5 + reasoning, N2+N9 compose) is included.

    visible_tokens = 5091-5000 = 91, expected_dense = 160/1.75 = 91.43, ratio=0.005 -> PASS.
    Persisted qa_passed=False; per-record pass + no sig -> included.
    """
    records = load_records(_FIXTURE_JSONL, "family", qa_only=True)
    ids = {r.informant_id for r in records}
    assert "rc-fix-r09-dense-and-reasoning" in ids


def test_r1_stay_excluded_still_failing():
    """R1 non-recovery: r03 (reasoning, 700k ms latency) remains excluded.

    700000 ms exceeds the reasoning ceiling (600000 ms). Per-record still fails.
    """
    records = load_records(_FIXTURE_JSONL, "family", qa_only=True)
    ids = {r.informant_id for r in records}
    assert "rc-fix-r03-reasoning-700k" not in ids


def test_r1_stay_excluded_check2_signature():
    """R1 stay-excluded-on-%-signature: r15 remains excluded despite per-record pass.

    r15: qa_passed=False, passes all per-record checks, but qa_notes='12.5%'.
    The bare-percentage signature indicates Check 2 contributed to the
    collection-time failure. Per N15, the persisted verdict is inherited;
    r15 is NOT recovered even though per-record checks now pass.
    """
    records = load_records(_FIXTURE_JSONL, "family", qa_only=True)
    ids = {r.informant_id for r in records}
    assert "rc-fix-r15-check2-sig" not in ids


def test_r1_included_unchanged_non_reasoning_record():
    """R1 included-unchanged: r01 (non-reasoning, persisted-True) is included.

    qa_passed=True and all per-record checks still pass -> included (no divergence).
    """
    records = load_records(_FIXTURE_JSONL, "family", qa_only=True)
    ids = {r.informant_id for r in records}
    assert "rc-fix-r01-nonreason" in ids


def test_r1_family_domain_count():
    """Family domain with qa_only=True returns exactly 5 records.

    Included: r01 (True->True), r02 (False->True recover), r04 (False->True),
              r08 (False->True dense), r09 (False->True dense+reasoning).
    Excluded: r03 (False, still fails latency), r15 (False, check2-sig).
    r05 no longer in family domain (moved to test_guard_1).
    """
    records = load_records(_FIXTURE_JSONL, "family", qa_only=True)
    assert len(records) == 5


# ─── R2: N16 monotonicity guard ───────────────────────────────────────────────


def test_r2_guard_raises_1_model_case():
    """N16 monotonicity guard: RuntimeError for 1 persisted-True record failing re-QA.

    test_guard_1 domain has r05: qa_passed=True, model=test/borderline-e, 5 items.
    Check 1 fires (5 < MIN_FREELIST_ITEMS=10). Persisted-True-now-False -> guard raises.
    Error message must name the model and record count.
    """
    with pytest.raises(RuntimeError) as exc_info:
        load_records(_FIXTURE_JSONL, "test_guard_1", qa_only=True)
    msg = str(exc_info.value)
    assert "N16 monotonicity guard" in msg
    assert "test/borderline-e" in msg
    assert "1 record(s)" in msg


def test_r2_guard_raises_2_model_case():
    """N16 monotonicity guard: RuntimeError enumerates 2 models on 2-model drop.

    test_guard_2 domain has r17 (test/borderline-e2, 5 items, True) and
    r18 (test/borderline-f, 5 items, True). Both fail Check 1. Error message
    must name both models.
    """
    with pytest.raises(RuntimeError) as exc_info:
        load_records(_FIXTURE_JSONL, "test_guard_2", qa_only=True)
    msg = str(exc_info.value)
    assert "N16 monotonicity guard" in msg
    assert "test/borderline-e2" in msg
    assert "test/borderline-f" in msg


def test_r2_guard_silent_at_zero_drops():
    """N16 monotonicity guard: no RuntimeError when no persisted-True record fails.

    Family domain (after r05 moved out): r01 is persisted-True and passes all
    per-record checks. No drops -> no exception.
    """
    records = load_records(_FIXTURE_JSONL, "family", qa_only=True)
    assert len(records) == 5  # No exception raised


def test_r2_guard_recoveries_never_trigger():
    """N16 monotonicity guard: recoveries (persisted-False-now-True) never raise.

    Family domain has 4 recovered records (r02, r04, r08, r09). Recoveries
    are logged at INFO only; they must NOT trigger RuntimeError.
    """
    records = load_records(_FIXTURE_JSONL, "family", qa_only=True)
    # If RuntimeError were raised, the assert would never be reached.
    recovered_ids = {
        "rc-fix-r02-reasoning-batchA",
        "rc-fix-r04-reasoning-eq-tokens",
        "rc-fix-r08-dense-sonnet5",
        "rc-fix-r09-dense-and-reasoning",
    }
    ids = {r.informant_id for r in records}
    assert recovered_ids.issubset(ids)


# ─── R1: reference-set independence ───────────────────────────────────────────


def test_r1_reference_set_independence(tmp_path: Path):
    """Check 2 does not fire in load_records even with many same-model runs.

    Creates two records with model_id='test/ref-model-x' and nearly identical
    free lists (zero uniqueness ratio). Under the OLD implementation
    (run_record_checks called with all_domain_records), Check 2 would fire:
    both records share items, uniqueness ratio = 0.5 < MIN_UNIQUENESS_RATIO=0.15
    would depend on the freelist composition. In any case, passing a two-record
    reference set exposes Check 2 to potential fire.

    Under the NEW implementation, run_record_checks is called with [record]
    (single-record reference set). Check 2's len(same_runs) == 1 < 2 self-guard
    fires, returning None. Both persisted-True records are included without error.
    """
    # Both records have identical freelist items (worst-case uniqueness scenario).
    base = {
        "domain_slug": "test_ref_ind",
        "run_index": 0,
        "collection_date": "2026-07-10T10:00:00.000000",
        "model_id": "test/ref-model-x",
        "model_version_returned": "test/ref-model-x-v1",
        "family": "test",
        "provider": "openrouter",
        "provider_request_id": "req-ref-ind-a",
        "knowledge_cutoff": None,
        "open_weights": False,
        "origin_country": "us",
        "alignment_method": None,
        "collection_method": "openrouter",
        "collection_mode": "single_pass",
        "api_endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "api_version": "1.0",
        "temperature": 0.7,
        "top_p": None,
        "max_tokens": 4096,
        "system_prompt": "",
        "freelist": {
            "prompt_verbatim": "List family terms.",
            "prompt_version": "v1",
            "response_verbatim": (
                "1. mother\n2. father\n3. sister\n4. brother\n5. aunt\n"
                "6. uncle\n7. grandmother\n8. grandfather\n9. cousin\n"
                "10. niece\n11. nephew\n12. son\n13. daughter\n14. wife\n15. husband"
            ),
            "thinking_verbatim": "",
            "response_object_json": {},
            "input_tokens": 50,
            "output_tokens": 40,
            "thoughts_token_count": 0,
            "latency_ms": 5000,
            "stop_reason": "end_turn",
            "parsed_items": ["mother", "father", "sister", "brother", "aunt",
                             "uncle", "grandmother", "grandfather", "cousin",
                             "niece", "nephew", "son", "daughter", "wife", "husband"],
            "parsed_raw_order": ["mother", "father", "sister", "brother", "aunt",
                                 "uncle", "grandmother", "grandfather", "cousin",
                                 "niece", "nephew", "son", "daughter", "wife", "husband"],
        },
        "pile_sort": {
            "prompt_verbatim": "", "prompt_version": "v1",
            "response_verbatim": "", "thinking_verbatim": "",
            "response_object_json": {}, "input_tokens": 0,
            "output_tokens": 0, "thoughts_token_count": 0,
            "latency_ms": 0, "stop_reason": "not_collected",
            "parsed_piles": [], "parsed_matrix": [], "item_source": "own_freelist",
        },
        "interview": {
            "prompt_verbatim": "", "prompt_version": "v1",
            "response_verbatim": "", "thinking_verbatim": "",
            "response_object_json": {}, "input_tokens": 0,
            "output_tokens": 0, "thoughts_token_count": 0,
            "latency_ms": 0, "stop_reason": "not_collected",
            "parsed_pile_labels": [],
        },
        "truncation_type": None,
        "truncation_n": 15,
        "max_possible_n": None,
        "context_window_exceeded": False,
        "capacity_note": "",
        "sha256_manifest": {
            "freelist_prompt": "aaa", "freelist_response": "bbb",
            "pilesort_prompt": "ccc", "pilesort_response": "ddd",
            "interview_prompt": "eee", "interview_response": "fff",
            "request_params": "ggg",
        },
        "qa_passed": True,
        "qa_notes": "",
    }
    record_a = dict(base)
    record_a["informant_id"] = "ref-ind-run-0"
    record_a["run_index"] = 0
    record_a["provider_request_id"] = "req-ref-ind-a"

    record_b = dict(base)
    record_b["informant_id"] = "ref-ind-run-1"
    record_b["run_index"] = 1
    record_b["provider_request_id"] = "req-ref-ind-b"

    tmp_jsonl = tmp_path / "ref_ind.jsonl"
    with open(tmp_jsonl, "w", encoding="utf-8") as f:
        f.write(json.dumps(record_a) + "\n")
        f.write(json.dumps(record_b) + "\n")

    # load_records passes [record] as reference set; Check 2 sees 1 run and
    # self-guards. Both records are persisted-True and pass per-record checks.
    # No RuntimeError, both included.
    records = load_records(tmp_jsonl, "test_ref_ind", qa_only=True)
    assert len(records) == 2, (
        f"Expected 2 records (Check 2 disabled by single-record ref set); "
        f"got {len(records)}. Check 2 may have been re-enabled accidentally."
    )
    included_ids = {r.informant_id for r in records}
    assert "ref-ind-run-0" in included_ids
    assert "ref-ind-run-1" in included_ids


# ─── has_check2_signature unit tests ─────────────────────────────────────────


def test_has_check2_signature_bare_percentage():
    """Bare percentage string matches the Check-2 signature predicate."""
    assert _has_check2_signature("12.5%") is True
    assert _has_check2_signature("8.0%") is True
    assert _has_check2_signature("100.0%") is True


def test_has_check2_signature_percentage_with_campaign_id():
    """Percentage segment in a multi-segment qa_notes is detected."""
    assert _has_check2_signature("12.5%; campaign_id=foo") is True
    assert _has_check2_signature("campaign_id=foo; 12.5%") is True


def test_has_check2_signature_non_percentage_strings():
    """Non-percentage qa_notes strings do not match."""
    # Check 1 actual: str(count)
    assert _has_check2_signature("5") is False
    # Check 5 actual: f"{latency_ms}ms"
    assert _has_check2_signature("257000ms") is False
    # Check 6 actual: str(actual_tokens)
    assert _has_check2_signature("100") is False
    # Check 7 actual: "empty"
    assert _has_check2_signature("empty") is False
    # Check 8 actual: f"label_count_mismatch:{n}/{m}"
    assert _has_check2_signature("label_count_mismatch:5/4") is False
    # Check 3 actual: f"found {cell}"
    assert _has_check2_signature("found 2") is False
    # Campaign ID only
    assert _has_check2_signature("campaign_id=reasoning_class_fixture") is False
    # Empty
    assert _has_check2_signature("") is False
    # Verbose descriptions (old fixture format, pre-runner.py format)
    assert _has_check2_signature(
        "Check 5 FAIL: freelist latency too high. Check 6 FAIL: inconsistent."
    ) is False


def test_has_check2_signature_integer_percent_no_decimal():
    """Integers followed by % (no decimal) do NOT match the Check-2 format.

    The runner.py format uses f"{ratio:.1%}" which always produces exactly
    one decimal digit (e.g. "8.0%", not "8%"). A bare "8%" is not a valid
    Check-2 signature.
    """
    assert _has_check2_signature("8%") is False
    assert _has_check2_signature("100%") is False


# ─── Divergence logging ───────────────────────────────────────────────────────


def test_divergence_logged_recovery_direction(caplog: pytest.LogCaptureFixture):
    """Divergence in the recovery direction is logged at INFO with correct count.

    Family domain (after r05 moved to test_guard_1):
    - persisted-True-now-False: 0 (r01 passes; no other persisted-True records)
    - persisted-False-now-True: 4 (r02, r04, r08, r09 recovered)
    - r15 has Check-2 sig: NOT counted in n_false_now_true (excluded by sig path)
    """
    with caplog.at_level(logging.INFO, logger="cdb_analyze.pipeline"):
        load_records(_FIXTURE_JSONL, "family", qa_only=True)

    log_text = " ".join(caplog.messages)
    assert "persisted-True-now-False: 0" in log_text
    assert "persisted-False-now-True: 4" in log_text


def test_check2_sig_exclusion_logged(caplog: pytest.LogCaptureFixture):
    """Check-2-signature exclusions are logged separately from QA divergence.

    r15 (family domain, bare % in qa_notes) is excluded by the Check-2
    signature guard. A dedicated INFO message must be logged.
    """
    with caplog.at_level(logging.INFO, logger="cdb_analyze.pipeline"):
        load_records(_FIXTURE_JSONL, "family", qa_only=True)

    log_text = " ".join(caplog.messages)
    # The message naming Check-2 signature exclusion must appear.
    assert "Check-2 signature" in log_text or "check2" in log_text.lower()


# ─── Edge cases ───────────────────────────────────────────────────────────────


def test_qa_only_true_zero_record_domain():
    """load_records with qa_only=True on a domain with no records returns []."""
    records = load_records(_FIXTURE_JSONL, "nonexistent_domain", qa_only=True)
    assert records == []


def test_run_record_checks_exception_propagates_from_load_records():
    """When run_record_checks raises mid-list, load_records propagates the exception."""
    with (
        patch("scripts.qa_check.run_record_checks", side_effect=RuntimeError("boom")),
        pytest.raises(RuntimeError, match="boom"),
    ):
        load_records(_FIXTURE_JSONL, "family", qa_only=True)


def test_malformed_jsonl_raises_json_decode_error():
    """A malformed JSONL line causes load_records to raise json.JSONDecodeError."""
    import json as _json  # noqa: PLC0415
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".jsonl", delete=False, encoding="utf-8"
    ) as f:
        f.write("this is not valid json\n")
        tmp_path = Path(f.name)

    try:
        with pytest.raises(_json.JSONDecodeError):
            load_records(tmp_path, "family", qa_only=False)
    finally:
        tmp_path.unlink(missing_ok=True)
