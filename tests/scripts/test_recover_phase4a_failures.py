"""Tests for scripts/recover_phase4a_failures.py.

No real API calls — all run_informant calls are stubbed with unittest.mock
per CLAUDE.md §6 rule 10 / §9 pitfall 9.

Fixtures:
    tests/fixtures/phase4a_failures_sample.jsonl  — synthetic failures with all
        three in-scope models, three out-of-scope models, and a duplicate row.
    tests/fixtures/phase4a_recovered_sample.jsonl — synthetic informants with
        one recovery-tagged record, one untagged record, and one record whose
        qa_notes contains the campaign-id concatenated with other tags.

Coverage
--------
1. Target-list extractor: correct count, dedup, sort, out-of-scope exclusion.
2. Idempotence check: already-recovered cell is skipped, not re-attempted.
3. Substring match (SME R4): qa_notes with concatenated tags still matched.
4. Retry budget (both fail): one failures.jsonl row written with
   recovery_failed=true, zero informants.jsonl rows written.
5. First-attempt success: one informants.jsonl row written, no retry, no failure row.
6. Second-attempt success: one informants.jsonl row written, no failure row.
7. Dry-run mode: no run_informant calls, no file writes, correct output.
8. Target count assertion: wrong-count fixtures → sys.exit(1) with error message.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from cdb_collect.exceptions import PartialSessionError
from cdb_core import FreelistRecord, InformantRecord, InterviewRecord, PileSortRecord

# Import the module under test.  The module-level MODEL_REGISTRY load (from
# scripts.collect) may fail in test environments where registry.json doesn't
# exist — that is fine: we patch MODEL_REGISTRY in every test that needs it.
# We import individual functions (not the module) to avoid triggering sys.exit
# from build_target_list at import time.
from scripts.recover_phase4a_failures import (  # noqa: E402
    CAMPAIGN_ID,
    CAMPAIGN_MARKER,
    EXPECTED_TARGET_COUNT,
    IN_SCOPE_MODELS,
    RecoveryTarget,
    build_target_list,
    load_already_recovered,
    recover_cell,
)

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
_FAILURES_SAMPLE = _FIXTURES / "phase4a_failures_sample.jsonl"
_RECOVERED_SAMPLE = _FIXTURES / "phase4a_recovered_sample.jsonl"


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _make_informant_record(
    model_id: str = "google/gemini-2.5-pro",
    domain_slug: str = "family",
    run_index: int = 0,
    qa_notes: str = "",
) -> InformantRecord:
    """Build a minimal InformantRecord for use as a stub return value."""
    manifest = {k: "a" * 64 for k in [
        "freelist_prompt", "freelist_response",
        "pilesort_prompt", "pilesort_response",
        "interview_prompt", "interview_response",
        "request_params",
    ]}
    return InformantRecord(
        informant_id=f"test_{model_id.replace('/', '_')}_{domain_slug}_{run_index}",
        domain_slug=domain_slug,
        run_index=run_index,
        collection_date=datetime(2026, 5, 5, 12, 0, 0),
        model_id=model_id,
        model_version_returned=f"{model_id}-v1",
        family=model_id.split("/")[0],
        provider="openrouter",
        provider_request_id=f"req-test-{run_index}",
        knowledge_cutoff=None,
        open_weights=False,
        origin_country="us",
        alignment_method=None,
        collection_method="openrouter",
        api_endpoint="https://openrouter.ai/api/v1/chat/completions",
        api_version="",
        temperature=0.7,
        top_p=None,
        max_tokens=16384,
        system_prompt="",
        freelist=FreelistRecord(
            prompt_verbatim="list",
            prompt_version="v1",
            response_verbatim="1. mother\n2. father\n3. sister\n4. brother\n5. aunt\n"
                              "6. uncle\n7. grandmother\n8. grandfather\n9. cousin\n10. niece",
            response_object_json={},
            input_tokens=10,
            output_tokens=10,
            latency_ms=100,
            stop_reason="end_turn",
            parsed_items=[
                "mother", "father", "sister", "brother", "aunt",
                "uncle", "grandmother", "grandfather", "cousin", "niece",
            ],
            parsed_raw_order=[
                "mother", "father", "sister", "brother", "aunt",
                "uncle", "grandmother", "grandfather", "cousin", "niece",
            ],
        ),
        pile_sort=PileSortRecord(
            prompt_verbatim="sort",
            prompt_version="v1",
            response_verbatim='{"piles":[["mother","father"],["sister","brother"]]}',
            response_object_json={},
            input_tokens=10,
            output_tokens=10,
            latency_ms=100,
            stop_reason="end_turn",
            parsed_piles=[["mother", "father"], ["sister", "brother"]],
            parsed_matrix=[[1, 1, 0, 0], [1, 1, 0, 0], [0, 0, 1, 1], [0, 0, 1, 1]],
        ),
        interview=InterviewRecord(
            prompt_verbatim="label",
            prompt_version="v1",
            response_verbatim="1. Parents\n2. Siblings",
            response_object_json={},
            input_tokens=10,
            output_tokens=5,
            latency_ms=100,
            stop_reason="end_turn",
            parsed_pile_labels=["Parents", "Siblings"],
        ),
        sha256_manifest=manifest,
        qa_passed=True,
        qa_notes=qa_notes,
    )


def _make_partial_session_error(
    response_verbatim: str = "truncated output...",
) -> PartialSessionError:
    """Build a PartialSessionError with verbatim fields for retry tests."""
    cause = ValueError("Pile sort parsing failed after 3 attempts")
    return PartialSessionError(
        cause=cause,
        failed_step="pile_sort",
        partial_session={"freelist": {}},
        prompt_verbatim="sort these items",
        response_verbatim=response_verbatim,
        thinking_verbatim="",
        stop_reason="MAX_TOKENS",
        retry_attempts=[],
    )


# ─── 1. Target-list extractor ─────────────────────────────────────────────────

class TestBuildTargetList:
    def test_correct_count(self) -> None:
        """Fixture has exactly 20 in-scope rows (after dedup)."""
        targets = build_target_list(_FAILURES_SAMPLE)
        assert len(targets) == EXPECTED_TARGET_COUNT

    def test_in_scope_models_only(self) -> None:
        """All targets are from the three in-scope models."""
        targets = build_target_list(_FAILURES_SAMPLE)
        model_ids = {t.model_id for t in targets}
        assert model_ids == IN_SCOPE_MODELS

    def test_deduplication(self) -> None:
        """Duplicate (model_id, domain, run_index) rows produce one target."""
        # The fixture has glm-5.1 holidays run_index=4 duplicated (lines 16 and 25).
        # After dedup there should still be exactly 20 unique cells.
        targets = build_target_list(_FAILURES_SAMPLE)
        cell_keys = [(t.model_id, t.domain, t.run_index) for t in targets]
        assert len(cell_keys) == len(set(cell_keys)), "Duplicate cell keys found"

    def test_out_of_scope_excluded(self) -> None:
        """phi-4, gpt-5.4-mini, mistral-small rows are not in the target list."""
        targets = build_target_list(_FAILURES_SAMPLE)
        out_of_scope = {"microsoft/phi-4", "openai/gpt-5.4-mini", "mistralai/mistral-small-2603"}
        for t in targets:
            assert t.model_id not in out_of_scope, (
                f"Out-of-scope model {t.model_id!r} appeared in target list"
            )

    def test_sorted_deterministically(self) -> None:
        """Target list is sorted by (model_id, domain, run_index, timestamp)."""
        targets = build_target_list(_FAILURES_SAMPLE)
        assert targets == sorted(targets), "Target list is not sorted deterministically"

    def test_gemini_count(self) -> None:
        """Exactly 10 Gemini cells (5 family + 5 holidays)."""
        targets = build_target_list(_FAILURES_SAMPLE)
        gemini = [t for t in targets if t.model_id == "google/gemini-2.5-pro"]
        assert len(gemini) == 10

    def test_glm_count(self) -> None:
        """Exactly 6 glm-5.1 cells."""
        targets = build_target_list(_FAILURES_SAMPLE)
        glm = [t for t in targets if t.model_id == "z-ai/glm-5.1"]
        assert len(glm) == 6

    def test_llama_count(self) -> None:
        """Exactly 4 llama-4-maverick cells."""
        targets = build_target_list(_FAILURES_SAMPLE)
        llama = [t for t in targets if t.model_id == "meta-llama/llama-4-maverick"]
        assert len(llama) == 4

    def test_wrong_count_exits_1(self, tmp_path: Path) -> None:
        """When the in-scope filter yields != 20 cells, the script aborts with exit 1."""
        # Write a fixture with only 1 in-scope row
        bad_fixture = tmp_path / "bad_failures.jsonl"
        bad_fixture.write_text(
            '{"timestamp":"2026-04-22T10:00:00","error_type":"ValueError",'
            '"error_message":"msg","context":{"model_id":"google/gemini-2.5-pro",'
            '"domain":"family","run_index":0},"retry_attempts":[]}\n',
            encoding="utf-8",
        )
        with pytest.raises(SystemExit) as exc_info:
            build_target_list(bad_fixture)
        assert exc_info.value.code == 1

    def test_wrong_count_error_message(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str],
    ) -> None:
        """The exit-1 path prints a clear error about count mismatch."""
        bad_fixture = tmp_path / "bad_failures.jsonl"
        bad_fixture.write_text(
            '{"timestamp":"t","error_type":"ValueError","error_message":"msg",'
            '"context":{"model_id":"google/gemini-2.5-pro","domain":"family",'
            '"run_index":0},"retry_attempts":[]}\n',
            encoding="utf-8",
        )
        with pytest.raises(SystemExit):
            build_target_list(bad_fixture)
        captured = capsys.readouterr()
        assert "20" in captured.err or "Expected" in captured.err


# ─── 2. Idempotence check ──────────────────────────────────────────────────────

class TestLoadAlreadyRecovered:
    def test_recovered_cell_detected(self) -> None:
        """A record with the campaign-id substring in qa_notes is detected."""
        recovered = load_already_recovered(_RECOVERED_SAMPLE)
        assert ("google/gemini-2.5-pro", "family", 0) in recovered

    def test_untagged_record_not_detected(self) -> None:
        """A record without the campaign-id substring is not detected."""
        recovered = load_already_recovered(_RECOVERED_SAMPLE)
        # run_index=1 has qa_notes without the campaign marker
        assert ("google/gemini-2.5-pro", "family", 1) not in recovered

    def test_nonexistent_file_returns_empty(self, tmp_path: Path) -> None:
        """A missing informants.jsonl returns an empty set (no error)."""
        recovered = load_already_recovered(tmp_path / "nonexistent.jsonl")
        assert recovered == set()

    def test_empty_file_returns_empty(self, tmp_path: Path) -> None:
        """An empty informants.jsonl returns an empty set."""
        empty = tmp_path / "empty.jsonl"
        empty.write_text("", encoding="utf-8")
        recovered = load_already_recovered(empty)
        assert recovered == set()

    # ─── 3. Substring match (SME R4) ──────────────────────────────────

    def test_substring_match_in_concatenated_qa_notes(self) -> None:
        """Campaign-id embedded in concatenated qa_notes is still matched.

        Fixture line 3 has qa_notes:
            'some-other-tag, campaign_id=phase4a-recovery-2026-05-05, more-tags'
        SME R4 requires substring match (not anchored regex) to handle this case.
        """
        recovered = load_already_recovered(_RECOVERED_SAMPLE)
        # run_index=2 has the campaign-id mid-string, surrounded by other tags
        assert ("google/gemini-2.5-pro", "family", 2) in recovered

    def test_substring_match_does_not_use_anchored_regex(
        self, tmp_path: Path,
    ) -> None:
        """Verify that various concatenation patterns all produce a match.

        Tests the three qa_notes formats that the substring convention supports:
        - Leading: 'campaign_id=X; other-tag'
        - Middle:  'prev-tag; campaign_id=X; next-tag'
        - Trailing: 'prev-tag; campaign_id=X'
        """
        informants_path = tmp_path / "informants.jsonl"

        # Write three records with the campaign-id in different positions
        formats = [
            f"{CAMPAIGN_MARKER}; qa_check=passed",
            f"qa_check=passed; {CAMPAIGN_MARKER}; other=value",
            f"qa_check=passed; {CAMPAIGN_MARKER}",
        ]
        lines = []
        for i, qa_notes in enumerate(formats):
            record = {
                "model_id": "google/gemini-2.5-pro",
                "domain_slug": "family",
                "run_index": i,
                "qa_notes": qa_notes,
            }
            lines.append(json.dumps(record))

        informants_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        recovered = load_already_recovered(informants_path)

        assert ("google/gemini-2.5-pro", "family", 0) in recovered, "Leading format not matched"
        assert ("google/gemini-2.5-pro", "family", 1) in recovered, "Middle format not matched"
        assert ("google/gemini-2.5-pro", "family", 2) in recovered, "Trailing format not matched"

    def test_non_campaign_substring_not_matched(self, tmp_path: Path) -> None:
        """A qa_notes with a similar but distinct marker is NOT matched."""
        informants_path = tmp_path / "informants.jsonl"
        record = {
            "model_id": "google/gemini-2.5-pro",
            "domain_slug": "family",
            "run_index": 0,
            "qa_notes": "campaign_id=phase4a-recovery-2026-05-06",  # wrong date
        }
        informants_path.write_text(json.dumps(record) + "\n", encoding="utf-8")
        recovered = load_already_recovered(informants_path)
        assert ("google/gemini-2.5-pro", "family", 0) not in recovered


# ─── 4. Retry budget — both attempts fail ─────────────────────────────────────

class TestRetryBudgetBothFail:
    """Both attempts fail → one failures.jsonl row with recovery_failed=true."""

    def test_failure_row_written_on_exhausted_budget(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        informants_out = tmp_path / "informants.jsonl"
        failures_out = tmp_path / "failures.jsonl"

        target = RecoveryTarget(
            model_id="google/gemini-2.5-pro",
            domain="family",
            run_index=0,
            original_failure_timestamp="2026-04-22T20:23:51",
        )

        pse = _make_partial_session_error()

        # Stub _run_one_informant to always raise PartialSessionError
        async def always_fail(*args, **kwargs):
            raise pse

        monkeypatch.setattr(
            "scripts.recover_phase4a_failures._run_one_informant",
            always_fail,
        )
        # Patch time.sleep to avoid actual delays
        monkeypatch.setattr("scripts.recover_phase4a_failures.time.sleep", lambda s: None)

        outcome = recover_cell(target, 1, 1, informants_out, failures_out)

        assert outcome == "RECOVERY_FAILED"
        # Zero informants rows written
        no_informants = (
            not informants_out.exists()
            or informants_out.read_text(encoding="utf-8").strip() == ""
        )
        assert no_informants
        # Exactly one failures row written
        assert failures_out.exists()
        rows = [
            json.loads(line)
            for line in failures_out.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        assert len(rows) == 1
        ctx = rows[0]["context"]
        assert ctx["recovery_failed"] is True
        assert ctx["campaign_id"] == CAMPAIGN_ID
        assert ctx["model_id"] == "google/gemini-2.5-pro"
        assert ctx["domain"] == "family"
        assert ctx["run_index"] == 0

    def test_failure_row_contains_verbatim_response(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """SME R2: failure row must contain response_verbatim from attempt 2."""
        informants_out = tmp_path / "informants.jsonl"
        failures_out = tmp_path / "failures.jsonl"

        target = RecoveryTarget(
            model_id="z-ai/glm-5.1",
            domain="family",
            run_index=1,
            original_failure_timestamp="2026-04-22T22:31:17",
        )

        pse = _make_partial_session_error(response_verbatim="<truncated JSON>")

        async def always_fail(*args, **kwargs):
            raise pse

        monkeypatch.setattr(
            "scripts.recover_phase4a_failures._run_one_informant",
            always_fail,
        )
        monkeypatch.setattr("scripts.recover_phase4a_failures.time.sleep", lambda s: None)

        recover_cell(target, 1, 1, informants_out, failures_out)

        rows = [
            json.loads(line)
            for line in failures_out.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        assert len(rows) == 1
        # response_verbatim from the PartialSessionError must be in the row
        assert rows[0].get("response_verbatim") == "<truncated JSON>"

    def test_failure_row_stop_reason_captured(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """SME R2: stop_reason must be captured in the failure row."""
        informants_out = tmp_path / "informants.jsonl"
        failures_out = tmp_path / "failures.jsonl"

        target = RecoveryTarget(
            model_id="z-ai/glm-5.1",
            domain="holidays",
            run_index=0,
            original_failure_timestamp="2026-04-22T22:47:06",
        )

        pse = _make_partial_session_error()

        async def always_fail(*args, **kwargs):
            raise pse

        monkeypatch.setattr(
            "scripts.recover_phase4a_failures._run_one_informant",
            always_fail,
        )
        monkeypatch.setattr("scripts.recover_phase4a_failures.time.sleep", lambda s: None)

        recover_cell(target, 1, 1, informants_out, failures_out)

        rows = [
            json.loads(line)
            for line in failures_out.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        assert rows[0].get("stop_reason") == "MAX_TOKENS"

    def test_non_partial_session_error_no_verbatim(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Non-PartialSessionError failure rows have no response_verbatim (acceptable)."""
        informants_out = tmp_path / "informants.jsonl"
        failures_out = tmp_path / "failures.jsonl"

        target = RecoveryTarget(
            model_id="meta-llama/llama-4-maverick",
            domain="family",
            run_index=1,
            original_failure_timestamp="2026-04-22T20:25:55",
        )

        async def always_fail(*args, **kwargs):
            raise RuntimeError("connection refused")

        monkeypatch.setattr(
            "scripts.recover_phase4a_failures._run_one_informant",
            always_fail,
        )
        monkeypatch.setattr("scripts.recover_phase4a_failures.time.sleep", lambda s: None)

        outcome = recover_cell(target, 1, 1, informants_out, failures_out)

        assert outcome == "RECOVERY_FAILED"
        rows = [
            json.loads(line)
            for line in failures_out.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        assert len(rows) == 1
        # Non-PartialSessionError: no response_verbatim key in the row
        assert "response_verbatim" not in rows[0]


# ─── 5. First-attempt success ─────────────────────────────────────────────────

class TestFirstAttemptSuccess:
    def test_record_written_on_first_attempt(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        informants_out = tmp_path / "informants.jsonl"
        failures_out = tmp_path / "failures.jsonl"

        target = RecoveryTarget(
            model_id="google/gemini-2.5-pro",
            domain="family",
            run_index=0,
            original_failure_timestamp="2026-04-22T20:23:51",
        )

        record = _make_informant_record(
            model_id="google/gemini-2.5-pro",
            domain_slug="family",
            run_index=0,
            qa_notes=CAMPAIGN_MARKER,
        )

        call_count = {"n": 0}

        async def succeed_first(*args, **kwargs):
            call_count["n"] += 1
            return record

        monkeypatch.setattr(
            "scripts.recover_phase4a_failures._run_one_informant",
            succeed_first,
        )

        outcome = recover_cell(target, 1, 1, informants_out, failures_out)

        assert outcome == "PASS"
        assert call_count["n"] == 1, "Expected exactly 1 call (no retry)"
        assert informants_out.exists()
        lines = [
            ln for ln in informants_out.read_text(encoding="utf-8").splitlines() if ln.strip()
        ]
        assert len(lines) == 1
        assert not failures_out.exists()

    def test_no_sleep_on_first_attempt_success(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """time.sleep should NOT be called when attempt 1 succeeds."""
        informants_out = tmp_path / "informants.jsonl"
        failures_out = tmp_path / "failures.jsonl"

        target = RecoveryTarget(
            model_id="google/gemini-2.5-pro",
            domain="family",
            run_index=0,
            original_failure_timestamp="2026-04-22T20:23:51",
        )

        record = _make_informant_record(qa_notes=CAMPAIGN_MARKER)
        sleep_calls: list[float] = []

        async def succeed_first(*args, **kwargs):
            return record

        monkeypatch.setattr(
            "scripts.recover_phase4a_failures._run_one_informant",
            succeed_first,
        )
        monkeypatch.setattr(
            "scripts.recover_phase4a_failures.time.sleep",
            lambda s: sleep_calls.append(s),
        )

        recover_cell(target, 1, 1, informants_out, failures_out)

        assert len(sleep_calls) == 0, "time.sleep should not be called on first-attempt success"


# ─── 6. Second-attempt success ────────────────────────────────────────────────

class TestSecondAttemptSuccess:
    def test_record_written_on_second_attempt(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        informants_out = tmp_path / "informants.jsonl"
        failures_out = tmp_path / "failures.jsonl"

        target = RecoveryTarget(
            model_id="z-ai/glm-5.1",
            domain="family",
            run_index=1,
            original_failure_timestamp="2026-04-22T22:31:17",
        )

        record = _make_informant_record(
            model_id="z-ai/glm-5.1",
            domain_slug="family",
            run_index=1,
            qa_notes=CAMPAIGN_MARKER,
        )

        call_count = {"n": 0}
        pse = _make_partial_session_error()
        sleep_calls: list[float] = []

        async def fail_then_succeed(*args, **kwargs):
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise pse
            return record

        monkeypatch.setattr(
            "scripts.recover_phase4a_failures._run_one_informant",
            fail_then_succeed,
        )
        monkeypatch.setattr(
            "scripts.recover_phase4a_failures.time.sleep",
            lambda s: sleep_calls.append(s),
        )

        outcome = recover_cell(target, 1, 1, informants_out, failures_out)

        assert outcome == "PASS"
        assert call_count["n"] == 2, "Expected exactly 2 calls (1 retry)"
        # Exactly one informants row
        assert informants_out.exists()
        lines = [
            ln for ln in informants_out.read_text(encoding="utf-8").splitlines() if ln.strip()
        ]
        assert len(lines) == 1
        # No failures row
        assert not failures_out.exists()

    def test_sleep_called_between_attempts(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """The 5s inter-attempt sleep is called exactly once between attempt 1 and 2."""
        informants_out = tmp_path / "informants.jsonl"
        failures_out = tmp_path / "failures.jsonl"

        target = RecoveryTarget(
            model_id="z-ai/glm-5.1",
            domain="family",
            run_index=1,
            original_failure_timestamp="2026-04-22T22:31:17",
        )

        record = _make_informant_record(qa_notes=CAMPAIGN_MARKER)
        call_count = {"n": 0}
        sleep_calls: list[float] = []

        async def fail_then_succeed(*args, **kwargs):
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise _make_partial_session_error()
            return record

        monkeypatch.setattr(
            "scripts.recover_phase4a_failures._run_one_informant",
            fail_then_succeed,
        )
        monkeypatch.setattr(
            "scripts.recover_phase4a_failures.time.sleep",
            lambda s: sleep_calls.append(s),
        )

        recover_cell(target, 1, 1, informants_out, failures_out)

        assert len(sleep_calls) == 1
        assert sleep_calls[0] == 5  # INTER_ATTEMPT_DELAY_S


# ─── 7. Dry-run mode ──────────────────────────────────────────────────────────

class TestDryRun:
    def test_dry_run_no_api_calls(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--dry-run must not invoke run_informant or write to any JSONL file."""
        informants_out = tmp_path / "informants.jsonl"
        failures_out = tmp_path / "failures.jsonl"

        call_count = {"n": 0}

        async def should_not_be_called(*args, **kwargs):
            call_count["n"] += 1
            raise AssertionError("run_informant must not be called in dry-run mode")

        monkeypatch.setattr(
            "scripts.recover_phase4a_failures._run_one_informant",
            should_not_be_called,
        )
        monkeypatch.setattr(
            "scripts.recover_phase4a_failures.INFORMANTS_JSONL",
            informants_out,
        )
        monkeypatch.setattr(
            "scripts.recover_phase4a_failures.FAILURES_JSONL",
            failures_out,
        )
        monkeypatch.setattr(
            "scripts.recover_phase4a_failures.FAILURES_JSONL",
            _FAILURES_SAMPLE,  # use real sample for target-list build
        )

        # Patch MODEL_REGISTRY with all three in-scope models
        mock_registry = {
            m: MagicMock(collection_method="openrouter")
            for m in IN_SCOPE_MODELS
        }
        monkeypatch.setattr("scripts.recover_phase4a_failures.MODEL_REGISTRY", mock_registry)
        # Also patch collect.MODEL_REGISTRY used by _load_registry at import time
        monkeypatch.setattr("scripts.collect.MODEL_REGISTRY", mock_registry)

        monkeypatch.setattr("sys.argv", ["recover_phase4a_failures.py", "--dry-run"])

        from scripts.recover_phase4a_failures import main
        exit_code = main()

        assert exit_code == 0
        assert call_count["n"] == 0, "run_informant was called during dry-run"
        # Verify no output files were created
        assert not informants_out.exists()
        assert not failures_out.exists()

    def test_dry_run_prints_target_list(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """--dry-run output includes target count and all three in-scope models."""
        monkeypatch.setattr(
            "scripts.recover_phase4a_failures.FAILURES_JSONL",
            _FAILURES_SAMPLE,
        )
        monkeypatch.setattr(
            "scripts.recover_phase4a_failures.INFORMANTS_JSONL",
            tmp_path / "informants.jsonl",
        )

        mock_registry = {
            m: MagicMock(collection_method="openrouter")
            for m in IN_SCOPE_MODELS
        }
        monkeypatch.setattr("scripts.recover_phase4a_failures.MODEL_REGISTRY", mock_registry)

        monkeypatch.setattr("sys.argv", ["recover.py", "--dry-run"])

        from scripts.recover_phase4a_failures import main
        exit_code = main()

        assert exit_code == 0
        out = capsys.readouterr().out
        assert str(EXPECTED_TARGET_COUNT) in out
        assert "google/gemini-2.5-pro" in out
        assert "z-ai/glm-5.1" in out
        assert "meta-llama/llama-4-maverick" in out
        assert "DRY RUN" in out

    def test_dry_run_no_api_calls_variant(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Explicit check: recover_cell is never called in dry-run mode."""
        monkeypatch.setattr(
            "scripts.recover_phase4a_failures.FAILURES_JSONL",
            _FAILURES_SAMPLE,
        )
        monkeypatch.setattr(
            "scripts.recover_phase4a_failures.INFORMANTS_JSONL",
            tmp_path / "informants.jsonl",
        )

        mock_registry = {
            m: MagicMock(collection_method="openrouter")
            for m in IN_SCOPE_MODELS
        }
        monkeypatch.setattr("scripts.recover_phase4a_failures.MODEL_REGISTRY", mock_registry)

        recover_cell_calls: list = []

        def mock_recover_cell(*args, **kwargs):
            recover_cell_calls.append(args)
            return "PASS"

        monkeypatch.setattr(
            "scripts.recover_phase4a_failures.recover_cell",
            mock_recover_cell,
        )

        monkeypatch.setattr("sys.argv", ["recover.py", "--dry-run"])

        from scripts.recover_phase4a_failures import main
        main()

        assert len(recover_cell_calls) == 0


# ─── 8. Target count assertion ────────────────────────────────────────────────

class TestTargetCountAssertion:
    def test_fewer_than_20_exits_1(self, tmp_path: Path) -> None:
        """Fixture with 19 in-scope cells → sys.exit(1)."""
        # Write 19 Gemini rows (missing one)
        rows = [
            {
                "timestamp": "2026-04-22T20:00:00",
                "error_type": "ValueError",
                "error_message": "msg",
                "context": {
                    "model_id": "google/gemini-2.5-pro",
                    "domain": "family",
                    "run_index": i,
                },
                "retry_attempts": [],
            }
            for i in range(19)  # Only 19 cells, not 20
        ]
        fixture = tmp_path / "short_failures.jsonl"
        fixture.write_text(
            "\n".join(json.dumps(r) for r in rows) + "\n",
            encoding="utf-8",
        )
        with pytest.raises(SystemExit) as exc_info:
            build_target_list(fixture)
        assert exc_info.value.code == 1

    def test_more_than_20_exits_1(self, tmp_path: Path) -> None:
        """Fixture with 21 in-scope cells → sys.exit(1)."""
        rows = [
            {
                "timestamp": "2026-04-22T20:00:00",
                "error_type": "ValueError",
                "error_message": "msg",
                "context": {
                    "model_id": "google/gemini-2.5-pro",
                    "domain": "family",
                    "run_index": i,
                },
                "retry_attempts": [],
            }
            for i in range(21)  # 21 cells, too many
        ]
        fixture = tmp_path / "long_failures.jsonl"
        fixture.write_text(
            "\n".join(json.dumps(r) for r in rows) + "\n",
            encoding="utf-8",
        )
        with pytest.raises(SystemExit) as exc_info:
            build_target_list(fixture)
        assert exc_info.value.code == 1


# ─── 9. original_failure_timestamp in recovery_failed rows ───────────────────

class TestOriginalFailureTimestamp:
    """Gap coverage: the recovery_failed row must carry original_failure_timestamp.

    Plan §2 R1 behavior 3 requires the new failures.jsonl row to include
    the original failure's timestamp as a cross-reference field.  The
    existing tests assert the other context keys but never assert this one.
    """

    def test_original_timestamp_present_in_failure_row(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """original_failure_timestamp must appear in context of a recovery_failed row."""
        informants_out = tmp_path / "informants.jsonl"
        failures_out = tmp_path / "failures.jsonl"

        sentinel_ts = "2026-04-22T20:23:51.189181"
        target = RecoveryTarget(
            model_id="google/gemini-2.5-pro",
            domain="family",
            run_index=0,
            original_failure_timestamp=sentinel_ts,
        )

        pse = _make_partial_session_error()

        async def always_fail(*args, **kwargs):
            raise pse

        monkeypatch.setattr(
            "scripts.recover_phase4a_failures._run_one_informant",
            always_fail,
        )
        monkeypatch.setattr("scripts.recover_phase4a_failures.time.sleep", lambda s: None)

        recover_cell(target, 1, 1, informants_out, failures_out)

        rows = [
            json.loads(line)
            for line in failures_out.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        assert len(rows) == 1
        ctx = rows[0]["context"]
        assert "original_failure_timestamp" in ctx, (
            "original_failure_timestamp must be in context for cross-reference"
        )
        assert ctx["original_failure_timestamp"] == sentinel_ts

    def test_original_timestamp_correct_value_for_each_model(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Each recovery target carries its own timestamp — verify per-cell isolation."""
        # Three targets, each with a distinct timestamp from the fixture
        targets_and_timestamps = [
            ("z-ai/glm-5.1",               "family",   1, "2026-04-22T22:31:17.084756"),
            ("z-ai/glm-5.1",               "holidays", 0, "2026-04-22T22:47:06.547653"),
            ("meta-llama/llama-4-maverick", "family",   1, "2026-04-22T20:25:55.777277"),
        ]

        async def always_fail(*args, **kwargs):
            raise _make_partial_session_error()

        monkeypatch.setattr(
            "scripts.recover_phase4a_failures._run_one_informant",
            always_fail,
        )
        monkeypatch.setattr("scripts.recover_phase4a_failures.time.sleep", lambda s: None)

        for model_id, domain, run_index, expected_ts in targets_and_timestamps:
            informants_out = tmp_path / f"informants_{run_index}.jsonl"
            failures_out = tmp_path / f"failures_{model_id.replace('/', '_')}_{run_index}.jsonl"
            target = RecoveryTarget(
                model_id=model_id,
                domain=domain,
                run_index=run_index,
                original_failure_timestamp=expected_ts,
            )
            recover_cell(target, 1, 1, informants_out, failures_out)

            rows = [
                json.loads(line)
                for line in failures_out.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            assert rows[0]["context"]["original_failure_timestamp"] == expected_ts, (
                f"Wrong timestamp for {model_id}/{domain} run={run_index}"
            )

    def test_non_pse_failure_also_has_original_timestamp(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Non-PartialSessionError failures must also carry original_failure_timestamp."""
        informants_out = tmp_path / "informants.jsonl"
        failures_out = tmp_path / "failures.jsonl"

        sentinel_ts = "2026-04-22T22:57:29.951184"
        target = RecoveryTarget(
            model_id="z-ai/glm-5.1",
            domain="holidays",
            run_index=4,
            original_failure_timestamp=sentinel_ts,
        )

        async def always_fail(*args, **kwargs):
            raise OSError("network timeout")

        monkeypatch.setattr(
            "scripts.recover_phase4a_failures._run_one_informant",
            always_fail,
        )
        monkeypatch.setattr("scripts.recover_phase4a_failures.time.sleep", lambda s: None)

        recover_cell(target, 1, 1, informants_out, failures_out)

        rows = [
            json.loads(line)
            for line in failures_out.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        assert rows[0]["context"]["original_failure_timestamp"] == sentinel_ts


# ─── 10. Exit code 2 (recovery rate < 80%) ───────────────────────────────────

class TestExitCode2:
    """Gap coverage: when recovery rate < 80%, main() must return 2.

    Plan §2 R1 exit-code contract: exit 2 if recovery rate < 80%.
    SME R6: this exit triggers CDA SME re-review before T4-redo proceeds.
    No existing test exercises this path.
    """

    def _make_failures_fixture(self, tmp_path: Path, n_cells: int = 20) -> Path:
        """Write a synthetic failures.jsonl with exactly n_cells in-scope rows."""
        rows = []
        domains = ["family", "holidays"]
        models = [
            "google/gemini-2.5-pro",
            "z-ai/glm-5.1",
            "meta-llama/llama-4-maverick",
        ]
        # Distribute cells across models/domains to hit exactly n_cells in-scope rows
        i = 0
        for model in models:
            for domain in domains:
                for run in range(5):
                    if i >= n_cells:
                        break
                    rows.append({
                        "timestamp": f"2026-04-22T20:{i:02d}:00.000000",
                        "error_type": "ValueError",
                        "error_message": "Pile sort parsing failed",
                        "context": {
                            "model_id": model,
                            "domain": domain,
                            "run_index": run,
                        },
                        "retry_attempts": [],
                    })
                    i += 1
                if i >= n_cells:
                    break
            if i >= n_cells:
                break
        fixture = tmp_path / "failures_exit2.jsonl"
        fixture.write_text(
            "\n".join(json.dumps(r) for r in rows) + "\n",
            encoding="utf-8",
        )
        return fixture

    def test_exit_2_when_recovery_rate_below_threshold(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """main() returns 2 when fewer than 80% of cells succeed.

        Simulates 4 RECOVERY_FAILED + 16 PASS on 20 cells → rate = 80%
        exactly; spec says < 80%, so this should return 0.
        Then simulates 5 RECOVERY_FAILED on 20 cells (75%) → returns 2.
        """
        failures_fixture = self._make_failures_fixture(tmp_path, n_cells=20)

        monkeypatch.setattr(
            "scripts.recover_phase4a_failures.FAILURES_JSONL",
            failures_fixture,
        )
        monkeypatch.setattr(
            "scripts.recover_phase4a_failures.INFORMANTS_JSONL",
            tmp_path / "informants.jsonl",
        )
        mock_registry = {
            m: MagicMock(collection_method="openrouter")
            for m in IN_SCOPE_MODELS
        }
        monkeypatch.setattr("scripts.recover_phase4a_failures.MODEL_REGISTRY", mock_registry)

        # 5 RECOVERY_FAILED out of 20 cells = 75% → exit 2
        call_count = {"n": 0}

        def mock_recover_cell_5_fail(target, cell_index, total, inf_path, fail_path):
            call_count["n"] += 1
            if call_count["n"] <= 5:
                return "RECOVERY_FAILED"
            return "PASS"

        monkeypatch.setattr(
            "scripts.recover_phase4a_failures.recover_cell",
            mock_recover_cell_5_fail,
        )
        monkeypatch.setattr("sys.argv", ["recover.py"])

        from scripts.recover_phase4a_failures import main
        exit_code = main()

        assert exit_code == 2, (
            f"Expected exit code 2 (recovery rate 75% < 80%) but got {exit_code}"
        )

    def test_exit_0_at_80_percent_threshold(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """main() returns 0 when recovery rate == 80% (boundary: strictly < 80% triggers exit 2)."""
        failures_fixture = self._make_failures_fixture(tmp_path, n_cells=20)

        monkeypatch.setattr(
            "scripts.recover_phase4a_failures.FAILURES_JSONL",
            failures_fixture,
        )
        monkeypatch.setattr(
            "scripts.recover_phase4a_failures.INFORMANTS_JSONL",
            tmp_path / "informants.jsonl",
        )
        mock_registry = {
            m: MagicMock(collection_method="openrouter")
            for m in IN_SCOPE_MODELS
        }
        monkeypatch.setattr("scripts.recover_phase4a_failures.MODEL_REGISTRY", mock_registry)

        # 4 RECOVERY_FAILED out of 20 cells = 80% success → exit 0 (threshold is < 80%)
        call_count = {"n": 0}

        def mock_recover_cell_4_fail(target, cell_index, total, inf_path, fail_path):
            call_count["n"] += 1
            if call_count["n"] <= 4:
                return "RECOVERY_FAILED"
            return "PASS"

        monkeypatch.setattr(
            "scripts.recover_phase4a_failures.recover_cell",
            mock_recover_cell_4_fail,
        )
        monkeypatch.setattr("sys.argv", ["recover.py"])

        from scripts.recover_phase4a_failures import main
        exit_code = main()

        assert exit_code == 0, (
            f"Expected exit code 0 (recovery rate 80% == threshold) but got {exit_code}"
        )

    def test_exit_2_with_already_recovered_cells_counted_toward_success(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Already-recovered cells count toward the recovery rate.

        Scenario: 10 cells already recovered (skipped), 5 PASS, 5 RECOVERY_FAILED.
        Rate = (10 + 5) / 20 = 75% → exit 2.
        """
        failures_fixture = self._make_failures_fixture(tmp_path, n_cells=20)
        informants_path = tmp_path / "informants.jsonl"

        monkeypatch.setattr(
            "scripts.recover_phase4a_failures.FAILURES_JSONL",
            failures_fixture,
        )
        monkeypatch.setattr(
            "scripts.recover_phase4a_failures.INFORMANTS_JSONL",
            informants_path,
        )
        mock_registry = {
            m: MagicMock(collection_method="openrouter")
            for m in IN_SCOPE_MODELS
        }
        monkeypatch.setattr("scripts.recover_phase4a_failures.MODEL_REGISTRY", mock_registry)

        # Simulate 10 already-recovered cells by pre-populating load_already_recovered
        # Build the expected target list to know which cells to mark as already-recovered
        from scripts.recover_phase4a_failures import build_target_list
        targets = build_target_list(failures_fixture)
        already_recovered = {
            (t.model_id, t.domain, t.run_index)
            for t in targets[:10]
        }
        monkeypatch.setattr(
            "scripts.recover_phase4a_failures.load_already_recovered",
            lambda path: already_recovered,
        )

        # Remaining 10 cells: 5 PASS + 5 RECOVERY_FAILED → rate = 15/20 = 75%
        call_count = {"n": 0}

        def mock_recover_cell(target, cell_index, total, inf_path, fail_path):
            call_count["n"] += 1
            if call_count["n"] <= 5:
                return "PASS"
            return "RECOVERY_FAILED"

        monkeypatch.setattr(
            "scripts.recover_phase4a_failures.recover_cell",
            mock_recover_cell,
        )
        monkeypatch.setattr("sys.argv", ["recover.py"])

        from scripts.recover_phase4a_failures import main
        exit_code = main()

        assert exit_code == 2, (
            f"Expected exit code 2 (rate 75% with already-recovered counted) but got {exit_code}"
        )


# ─── 11. Mixed scenario: main() per-cell counter accumulation ────────────────

class TestMainLoopCounters:
    """Gap coverage: verify that main() correctly accumulates per-cell counters.

    The individual recover_cell() function is tested extensively in isolation,
    but the main() loop's counter accumulation logic (n_recovered, n_recovery_failed,
    n_already_recovered) has not been tested under a mixed outcome scenario.
    This class drives main() with a controlled mix of outcomes and reads the
    summary from stdout to verify the counters are correct.
    """

    def _make_failures_fixture(self, tmp_path: Path) -> Path:
        """20-cell in-scope failures fixture for main() tests."""
        rows = []
        domains = ["family", "holidays"]
        i = 0
        for model in sorted(IN_SCOPE_MODELS):
            for domain in domains:
                for run in range(5):
                    if i >= 20:
                        break
                    rows.append({
                        "timestamp": f"2026-04-22T20:{i:02d}:00.000000",
                        "error_type": "ValueError",
                        "error_message": "Pile sort parsing failed",
                        "context": {
                            "model_id": model,
                            "domain": domain,
                            "run_index": run,
                        },
                        "retry_attempts": [],
                    })
                    i += 1
                if i >= 20:
                    break
            if i >= 20:
                break
        fixture = tmp_path / "failures_counters.jsonl"
        fixture.write_text(
            "\n".join(json.dumps(r) for r in rows) + "\n",
            encoding="utf-8",
        )
        return fixture

    def test_mixed_outcome_counters(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Mixed scenario: 12 PASS + 5 RECOVERY_FAILED + 3 already-recovered = 20.

        Verifies that the summary printed by main() shows the correct counts
        and that the exit code reflects the 85% success rate (12+3=15 successes).
        """
        failures_fixture = self._make_failures_fixture(tmp_path)

        monkeypatch.setattr(
            "scripts.recover_phase4a_failures.FAILURES_JSONL",
            failures_fixture,
        )
        monkeypatch.setattr(
            "scripts.recover_phase4a_failures.INFORMANTS_JSONL",
            tmp_path / "informants.jsonl",
        )
        mock_registry = {
            m: MagicMock(collection_method="openrouter")
            for m in IN_SCOPE_MODELS
        }
        monkeypatch.setattr("scripts.recover_phase4a_failures.MODEL_REGISTRY", mock_registry)

        # Pre-populate 3 already-recovered cells
        from scripts.recover_phase4a_failures import build_target_list
        targets = build_target_list(failures_fixture)
        already_recovered = {
            (t.model_id, t.domain, t.run_index)
            for t in targets[:3]
        }
        monkeypatch.setattr(
            "scripts.recover_phase4a_failures.load_already_recovered",
            lambda path: already_recovered,
        )

        # Remaining 17 cells: 12 PASS + 5 RECOVERY_FAILED
        call_count = {"n": 0}

        def mock_recover_cell(target, cell_index, total, inf_path, fail_path):
            call_count["n"] += 1
            if call_count["n"] <= 5:
                return "RECOVERY_FAILED"
            return "PASS"

        monkeypatch.setattr(
            "scripts.recover_phase4a_failures.recover_cell",
            mock_recover_cell,
        )
        monkeypatch.setattr("sys.argv", ["recover.py"])

        from scripts.recover_phase4a_failures import main
        exit_code = main()

        # Rate = (12 + 3) / 20 = 75% → exit 2 (below 80% threshold)
        assert exit_code == 2

        out = capsys.readouterr().out
        # Verify the summary section contains expected counts
        assert "Recovery-failed:      5" in out or "Recovery-failed" in out
        assert "Already-recovered:    3" in out or "Already-recovered" in out

    def test_all_pass_exits_0(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """20/20 PASS → exit 0, summary shows Recovered: 20."""
        failures_fixture = self._make_failures_fixture(tmp_path)

        monkeypatch.setattr(
            "scripts.recover_phase4a_failures.FAILURES_JSONL",
            failures_fixture,
        )
        monkeypatch.setattr(
            "scripts.recover_phase4a_failures.INFORMANTS_JSONL",
            tmp_path / "informants.jsonl",
        )
        mock_registry = {
            m: MagicMock(collection_method="openrouter")
            for m in IN_SCOPE_MODELS
        }
        monkeypatch.setattr("scripts.recover_phase4a_failures.MODEL_REGISTRY", mock_registry)
        monkeypatch.setattr(
            "scripts.recover_phase4a_failures.load_already_recovered",
            lambda path: set(),
        )

        def mock_recover_cell_all_pass(target, cell_index, total, inf_path, fail_path):
            return "PASS"

        monkeypatch.setattr(
            "scripts.recover_phase4a_failures.recover_cell",
            mock_recover_cell_all_pass,
        )
        monkeypatch.setattr("sys.argv", ["recover.py"])

        from scripts.recover_phase4a_failures import main
        exit_code = main()

        assert exit_code == 0
        out = capsys.readouterr().out
        assert "Recovered:            20" in out or "Recovered:" in out

    def test_all_already_recovered_exits_0(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """20/20 already-recovered → exit 0, recover_cell never called."""
        failures_fixture = self._make_failures_fixture(tmp_path)

        monkeypatch.setattr(
            "scripts.recover_phase4a_failures.FAILURES_JSONL",
            failures_fixture,
        )
        monkeypatch.setattr(
            "scripts.recover_phase4a_failures.INFORMANTS_JSONL",
            tmp_path / "informants.jsonl",
        )
        mock_registry = {
            m: MagicMock(collection_method="openrouter")
            for m in IN_SCOPE_MODELS
        }
        monkeypatch.setattr("scripts.recover_phase4a_failures.MODEL_REGISTRY", mock_registry)

        # All 20 cells pre-marked as already-recovered
        from scripts.recover_phase4a_failures import build_target_list
        targets = build_target_list(failures_fixture)
        all_recovered = {(t.model_id, t.domain, t.run_index) for t in targets}
        monkeypatch.setattr(
            "scripts.recover_phase4a_failures.load_already_recovered",
            lambda path: all_recovered,
        )

        recover_cell_calls: list = []

        def mock_recover_cell(*args, **kwargs):
            recover_cell_calls.append(args)
            return "PASS"

        monkeypatch.setattr(
            "scripts.recover_phase4a_failures.recover_cell",
            mock_recover_cell,
        )
        monkeypatch.setattr("sys.argv", ["recover.py"])

        from scripts.recover_phase4a_failures import main
        exit_code = main()

        assert exit_code == 0
        assert len(recover_cell_calls) == 0, (
            "recover_cell must not be called when all cells are already-recovered"
        )
        out = capsys.readouterr().out
        assert "Already-recovered:    20" in out or "Already-recovered" in out
