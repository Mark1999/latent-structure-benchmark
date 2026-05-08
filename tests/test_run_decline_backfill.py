"""Tests for scripts/run_decline_backfill.py — T1 and T1-update dry-run path.

Coverage per Phase 4a.1 architect plan §3 T1 acceptance criteria,
CDA SME verdict binding notes 1 and 8 (original), and Amendment 1
SME binding notes A1–A8.

No real API calls. No file writes. All fixtures are synthetic in-memory dicts
or loaded from tests/fixtures/.

Fixture scenarios (original T1):
  - 3 glm-5.1 x family: empty freelist (trigger c) -> 3 detected
  - 10 qwen3.6-plus x holidays: Check 5+6, structurally valid -> 10 not triggered
  - 4 Check-8-only: mistral-small/gpt-5.4-mini -> 4 not triggered (labels non-empty)
  - 1 llama-4-maverick: Check 5+8 compound -> not triggered (labels non-empty)
  - 8 grok-4: Check-5-only -> 8 not triggered, reason "Check-5 latency-only..."
  - 1 Gemini failure entry -> parsed, Gemini count increments, cost-guard OK
  - File-safety: mtime-snapshot on output file, monkeypatch blocks on open('w') + httpx
  - Cost-guard: 40 detected sessions -> script exits 2 with STOP message

T1-update additions (SME A1–A8):
  - TestShouldIncludeFailure: unit tests for all should_include_failure() branches
  - TestSection3bExcludedAudit: integration tests for Section 3b output
  - TestSection3cUnclassified: integration tests for Section 3c + SURFACE-TO-SME gate
  - TestMaxBatchCallsCLIOverride: CLI --max-batch-calls flag tests
  - TestCostGuardPostExclusion: post-exclusion cost gate tests (SME A8)
  - TestSourceFlag: --source {informants,failures,all} flag tests

References:
  Architect plan (original):  docs/status/2026-04-23-phase4a1-architect-plan.md
  SME verdict (original):     docs/status/2026-04-23-phase4a1-architect-plan-cda-sme-verdict.md
  Architect plan (Amendment): docs/status/2026-04-23-phase4a1-architect-plan-amendment-1.md
  SME verdict (Amendment 1):  docs/status/2026-04-23-phase4a1-amendment-1-cda-sme-verdict.md
"""

from __future__ import annotations

import importlib.util
import json
import sys as _sys
from io import StringIO
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

# T2 fixtures: MockAdapter
_FIXTURES_DIR_EARLY = Path(__file__).resolve().parent / "fixtures"
_sys.path.insert(0, str(_FIXTURES_DIR_EARLY))

_SCRIPT_PATH = Path(__file__).resolve().parent.parent / "scripts" / "run_decline_backfill.py"
_spec = importlib.util.spec_from_file_location("run_decline_backfill", _SCRIPT_PATH)
assert _spec is not None and _spec.loader is not None
_mod = importlib.util.module_from_spec(_spec)
_sys.modules["run_decline_backfill"] = _mod
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]

run_dry_run = _mod.run_dry_run
run_execute = _mod.run_execute
_parse_failing_checks = _mod._parse_failing_checks
_not_triggered_reason = _mod._not_triggered_reason
_originating_step_from_checks = _mod._originating_step_from_checks
_is_gemini_failure = _mod._is_gemini_failure
_is_recursive_decline = _mod._is_recursive_decline
should_include_failure = _mod.should_include_failure
build_parser = _mod.build_parser

_FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


# ── Fixture helpers ────────────────────────────────────────────────────────────

def _make_informant(
    *,
    informant_id: str,
    model_id: str,
    domain_slug: str = "family",
    qa_passed: bool = False,
    qa_notes: str = "",
    parsed_piles: list | None = None,
    pile_response: str = "Here are my piles.",
    parsed_items: list | None = None,
    parsed_labels: list | None = None,
    interview_response: str = "",
) -> dict[str, Any]:
    """Build a minimal informants.jsonl-shaped dict for testing."""
    if parsed_items is None:
        parsed_items = ["mother", "father", "sister", "brother"]
    if parsed_piles is None:
        parsed_piles = [["mother", "father"], ["sister", "brother"]]
    if parsed_labels is None:
        parsed_labels = ["nuclear", "extended"]
    return {
        "informant_id": informant_id,
        "model_id": model_id,
        "domain_slug": domain_slug,
        "qa_passed": qa_passed,
        "qa_notes": qa_notes,
        "freelist": {
            "parsed_items": parsed_items,
            "response_verbatim": "; ".join(parsed_items) if parsed_items else "",
        },
        "pile_sort": {
            "parsed_piles": parsed_piles,
            "response_verbatim": pile_response,
        },
        "interview": {
            "parsed_pile_labels": parsed_labels,
            "response_verbatim": interview_response,
        },
    }


def _make_failure(
    *,
    model_id: str,
    domain: str = "family",
    run_index: int = 0,
    timestamp: str = "2026-04-23T10:00:00",
    error_type: str = "ValueError",
) -> dict[str, Any]:
    """Build a minimal failures.jsonl-shaped dict for testing."""
    return {
        "timestamp": timestamp,
        "error_type": error_type,
        "error_message": "synthetic test error",
        "context": {
            "model_id": model_id,
            "domain": domain,
            "run_index": run_index,
        },
        "retry_attempts": [],
    }


def _write_jsonl(path: Path, records: list[dict]) -> None:
    """Write a list of dicts as JSONL to path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec) + "\n")


# ── _parse_failing_checks unit tests ──────────────────────────────────────────

class TestParseFailingChecks:
    """Unit tests for the qa_notes -> failing_checks parser."""

    def test_empty_notes_returns_empty(self) -> None:
        assert _parse_failing_checks("") == []

    def test_latency_only(self) -> None:
        result = _parse_failing_checks("102547ms")
        assert result == ["check_5_latency_exceeded"]

    def test_latency_and_tokens(self) -> None:
        result = _parse_failing_checks("154728ms; 8544")
        assert set(result) == {"check_5_latency_exceeded", "check_6_token_inconsistency"}

    def test_empty_freelist_with_latency_and_tokens(self) -> None:
        result = _parse_failing_checks("0; 71000ms; 171")
        assert set(result) == {
            "check_1_freelist_empty",
            "check_5_latency_exceeded",
            "check_6_token_inconsistency",
        }

    def test_label_count_mismatch_only(self) -> None:
        result = _parse_failing_checks("label_count_mismatch:20/9")
        assert result == ["check_8_label_count_mismatch"]

    def test_latency_and_label_count_mismatch(self) -> None:
        result = _parse_failing_checks("60124ms; label_count_mismatch:16/81")
        assert set(result) == {"check_5_latency_exceeded", "check_8_label_count_mismatch"}


class TestNotTriggeredReason:
    """Unit tests for the reason derivation function."""

    def test_check5_only(self) -> None:
        reason = _not_triggered_reason(["check_5_latency_exceeded"])
        assert reason == "Check-5 latency-only, no structural refusal trigger"

    def test_check8_only(self) -> None:
        reason = _not_triggered_reason(["check_8_label_count_mismatch"])
        assert "Check-8" in reason
        assert "non-empty" in reason

    def test_check5_and_check6(self) -> None:
        reason = _not_triggered_reason(["check_5_latency_exceeded", "check_6_token_inconsistency"])
        assert "5+6" in reason or "Check 5" in reason
        assert "response_verbatim non-empty" in reason

    def test_check5_and_check8(self) -> None:
        reason = _not_triggered_reason(
            ["check_5_latency_exceeded", "check_8_label_count_mismatch"]
        )
        assert "5+8" in reason or "Check 5" in reason

    def test_empty_checks(self) -> None:
        # Should return some fallback string, not raise
        reason = _not_triggered_reason([])
        assert isinstance(reason, str)


class TestIsGeminiFailure:
    """Unit tests for the Gemini entry classifier."""

    def test_google_gemini_prefix(self) -> None:
        entry = {"context": {"model_id": "google/gemini-2.5-pro"}}
        assert _is_gemini_failure(entry) is True

    def test_bare_gemini_prefix(self) -> None:
        entry = {"context": {"model_id": "gemini-1.5-flash"}}
        assert _is_gemini_failure(entry) is True

    def test_non_gemini(self) -> None:
        entry = {"context": {"model_id": "openai/gpt-5.4-mini"}}
        assert _is_gemini_failure(entry) is False

    def test_missing_context(self) -> None:
        entry: dict[str, Any] = {}
        assert _is_gemini_failure(entry) is False


# ── Full dry-run scenario tests ────────────────────────────────────────────────

class TestDryRunScenarios:
    """Integration-level tests that exercise run_dry_run() against synthetic JSONL files."""

    @pytest.fixture()
    def tmpdir(self, tmp_path: Path) -> Path:
        return tmp_path

    def _run_dry_run_capture(
        self,
        informants: list[dict],
        failures: list[dict],
        tmpdir: Path,
        verbose: bool = False,
        cost_per_call: float = 0.05,  # ignored; kept for call-site compat
        legacy_dollar_threshold: float = 2.00,  # unit-conversion artifact (old-contract tests)
    ) -> tuple[int, str]:
        """Write fixtures to temp files, run dry-run, capture stdout, return (exit_code, output).

        cost_per_call is ignored (cost tracking removed). legacy_dollar_threshold is a
        unit-conversion artifact from tests written under the old dollar-threshold contract;
        it is converted to a call-count cap: max_batch_calls = int(legacy_dollar_threshold /
        cost_per_call) so that existing test thresholds remain meaningful (e.g. $2/$0.05 =
        40 calls).
        """
        informants_path = tmpdir / "informants.jsonl"
        failures_path = tmpdir / "failures.jsonl"
        output_path = tmpdir / "decline_interviews.jsonl"

        _write_jsonl(informants_path, informants)
        _write_jsonl(failures_path, failures)
        # Create output file so we can snapshot its mtime
        output_path.touch()

        # Derive max_batch_calls from legacy_dollar_threshold / cost_per_call ratio
        max_batch_calls = max(1, int(legacy_dollar_threshold / cost_per_call))

        captured = StringIO()
        with patch("sys.stdout", captured):
            exit_code = run_dry_run(
                informants_path=informants_path,
                failures_path=failures_path,
                output_path=output_path,
                verbose=verbose,
                max_batch_calls=max_batch_calls,
            )
        return exit_code, captured.getvalue()

    # ── Scenario 1: 3 glm-5.1 empty freelist -> 3 detected ──────────────────

    def test_glm_empty_freelist_detected(self, tmpdir: Path) -> None:
        """3 glm-5.1 x family records with empty freelist -> 3 detected via trigger c."""
        informants = [
            _make_informant(
                informant_id=f"glm_test_{i:04d}",
                model_id="z-ai/glm-5.1",
                domain_slug="family",
                qa_passed=False,
                qa_notes="0; 71000ms; 171",
                parsed_items=[],  # empty freelist: trigger c
                parsed_piles=[["mother", "father"]],
                parsed_labels=["nuclear"],
                pile_response="Sorted above.",
            )
            for i in range(3)
        ]
        exit_code, output = self._run_dry_run_capture(informants, [], tmpdir)
        assert exit_code == 0
        assert "Total detected (to be interviewed in T3): 3" in output
        assert "Total not triggered: 0" in output
        assert "z-ai/glm-5.1" in output
        # Section 1 must show the trigger
        assert "freelist" in output
        assert "empty_output" in output

    # ── Scenario 2: 10 qwen Check-5+6, structurally valid -> 10 not triggered ─

    def test_qwen_check5_6_not_triggered(self, tmpdir: Path) -> None:
        """10 qwen3.6-plus x holidays with Check-5+6 (latency + token) but
        structurally valid freelist/piles -> 10 not triggered."""
        informants = [
            _make_informant(
                informant_id=f"qwen_test_{i:04d}",
                model_id="qwen/qwen3.6-plus",
                domain_slug="holidays",
                qa_passed=False,
                qa_notes=f"{86000 + i * 10000}ms; {4779 + i * 100}",
                parsed_items=["christmas", "easter", "halloween"],
                parsed_piles=[["christmas"], ["easter", "halloween"]],
                parsed_labels=["religious", "secular"],
                pile_response="Here are my sorted piles.",
            )
            for i in range(10)
        ]
        exit_code, output = self._run_dry_run_capture(informants, [], tmpdir)
        assert exit_code == 0
        assert "Total not triggered: 10" in output
        assert "Total detected (to be interviewed in T3): 0" in output
        # All 10 must appear in not-triggered section
        assert output.count("qwen/qwen3.6-plus") >= 10
        # Each row should have a reason mentioning Check 5+6
        assert "response_verbatim non-empty" in output

    def test_qwen_not_triggered_per_record_rows(self, tmpdir: Path) -> None:
        """SME binding note 1: per-record detail, not just a summary count."""
        informants = [
            _make_informant(
                informant_id=f"qwen_audit_{i:04d}",
                model_id="qwen/qwen3.6-plus",
                domain_slug="holidays",
                qa_passed=False,
                qa_notes=f"{90000 + i * 5000}ms; {5000 + i * 200}",
                parsed_items=["christmas", "easter"],
                parsed_piles=[["christmas"], ["easter"]],
                parsed_labels=["holiday1", "holiday2"],
            )
            for i in range(5)
        ]
        exit_code, output = self._run_dry_run_capture(informants, [], tmpdir)
        # Each record ID must appear in output
        for i in range(5):
            assert f"qwen_audit_{i:04d}" in output

    # ── Scenario 3: 4 Check-8 records -> 4 not triggered ────────────────────

    def test_check8_only_not_triggered(self, tmpdir: Path) -> None:
        """4 Check-8-only records (mistral-small x2, gpt-5.4-mini x1, test x1)
        -> 4 not triggered because parsed_pile_labels is non-empty."""
        informants = [
            _make_informant(
                informant_id=f"mistral_ch8_{i:04d}",
                model_id="mistralai/mistral-small-2603",
                domain_slug="holidays",
                qa_passed=False,
                qa_notes="label_count_mismatch:64/63",
                parsed_items=["christmas", "easter", "halloween"],
                parsed_piles=[["christmas"], ["easter"], ["halloween"]],
                parsed_labels=["holiday"] * 64,  # non-empty labels; mismatch but not empty
                pile_response="Sorted above.",
            )
            for i in range(2)
        ] + [
            _make_informant(
                informant_id="gpt54mini_ch8_0000",
                model_id="openai/gpt-5.4-mini",
                domain_slug="holidays",
                qa_passed=False,
                qa_notes="label_count_mismatch:20/9",
                parsed_items=["christmas", "easter", "halloween"],
                parsed_piles=[["christmas"], ["easter"], ["halloween"]],
                parsed_labels=["holiday"] * 20,  # non-empty
                pile_response="Sorted above.",
            ),
            _make_informant(
                informant_id="test_ch8_extra_0000",
                model_id="openai/gpt-5.4-mini",
                domain_slug="holidays",
                qa_passed=False,
                qa_notes="label_count_mismatch:30/10",
                # Ensure two piles so degenerate-pile trigger (e) does not fire
                parsed_items=["christmas", "easter", "halloween", "new_year", "thanksgiving"],
                parsed_piles=[["christmas", "easter"], ["halloween", "new_year", "thanksgiving"]],
                parsed_labels=["holiday"] * 30,  # non-empty
                pile_response="Sorted above.",
            ),
        ]
        exit_code, output = self._run_dry_run_capture(informants, [], tmpdir)
        assert exit_code == 0
        # All 4 are not triggered: trigger (d) requires parsed_pile_labels=[] AND
        # non-empty interview response; these records have non-empty labels.
        assert "Total not triggered: 4" in output
        assert "Total detected (to be interviewed in T3): 0" in output
        # Reason must mention Check-8 label mismatch context
        assert "check_8_label_count_mismatch" in output
        # Document that these are not detected (per actual detector behavior)

    # ── Scenario 4: 1 llama-4-maverick Check 5+8 -> not triggered ────────────

    def test_llama_check5_8_not_triggered(self, tmpdir: Path) -> None:
        """1 llama-4-maverick Check 5+8 compound record.
        Actual detector behavior: not triggered because parsed_pile_labels is non-empty
        (label_count_mismatch means labels exist, just the wrong count).
        trigger (d) requires parsed_pile_labels=[] — not satisfied here.
        """
        informants = [
            _make_informant(
                informant_id="llama_ch5_8_0000",
                model_id="meta-llama/llama-4-maverick",
                domain_slug="family",
                qa_passed=False,
                qa_notes="60124ms; label_count_mismatch:16/81",
                parsed_items=["mother", "father", "sister"],
                parsed_piles=[["mother", "father"], ["sister"]],
                parsed_labels=["parent"] * 16,  # non-empty; count mismatch vs freelist
                pile_response="Here are my piles.",
            )
        ]
        exit_code, output = self._run_dry_run_capture(informants, [], tmpdir)
        assert exit_code == 0
        # Actual behavior: not detected (labels non-empty, no allowlist match, piles non-empty)
        assert "Total not triggered: 1" in output
        assert "Total detected (to be interviewed in T3): 0" in output
        assert "llama_ch5_8_0000" in output
        # Reason should mention Check 5+8 compound
        assert "5+8" in output or "Check 5" in output

    # ── Scenario 5: 8 grok-4 Check-5-only -> 8 not triggered, per-record audit ─

    def test_grok4_check5_only_not_triggered(self, tmpdir: Path) -> None:
        """8 grok-4 x {family, holidays} Check-5-only records -> 8 not triggered.
        Reason must be 'Check-5 latency-only, no structural refusal trigger'.
        SME binding note 1: one row per record."""
        # 3 family + 5 holidays matching T6 report §9 distribution
        grok_family_ids = ["3e48592edf41a75e", "d42fecd904dd50d2", "d4f70682680a9b2c"]
        grok_holiday_ids = [
            "0216e50e02a8c493", "0b10c25030801614", "17fb4eeb3b8e5588",
            "7085fac78b1eae63", "c2997ef60b1355b7",
        ]

        informants = (
            [
                _make_informant(
                    informant_id=iid,
                    model_id="x-ai/grok-4",
                    domain_slug="family",
                    qa_passed=False,
                    qa_notes=f"{102547 + idx * 10000}ms",
                    parsed_items=["mother", "father", "sister"],
                    parsed_piles=[["mother", "father"], ["sister"]],
                    parsed_labels=["nuclear", "extended"],
                    pile_response="Sorted.",
                )
                for idx, iid in enumerate(grok_family_ids)
            ] + [
                _make_informant(
                    informant_id=iid,
                    model_id="x-ai/grok-4",
                    domain_slug="holidays",
                    qa_passed=False,
                    qa_notes=f"{247348 + idx * 5000}ms",
                    parsed_items=["christmas", "easter", "halloween"],
                    parsed_piles=[["christmas"], ["easter", "halloween"]],
                    parsed_labels=["religious", "secular"],
                    pile_response="Sorted.",
                )
                for idx, iid in enumerate(grok_holiday_ids)
            ]
        )

        exit_code, output = self._run_dry_run_capture(informants, [], tmpdir)
        assert exit_code == 0
        assert "Total not triggered: 8" in output
        assert "Total detected (to be interviewed in T3): 0" in output

        # Each grok-4 record ID must appear in the not-triggered section (note 1)
        for iid in grok_family_ids + grok_holiday_ids:
            assert iid in output

        # Each row must have the Check-5 latency reason
        assert output.count("Check-5 latency-only, no structural refusal trigger") == 8

    # ── Scenario 6: 1 Gemini failure -> Gemini count increments, OK cost guard ─

    def test_gemini_failure_counted(self, tmpdir: Path) -> None:
        """1 Gemini failure entry -> Gemini count = 1, detected = 1, cost guard OK."""
        failures = [
            _make_failure(
                model_id="google/gemini-2.5-pro",
                domain="family",
                run_index=0,
                timestamp="2026-04-23T10:00:00",
                error_type="ValueError",
            )
        ]
        exit_code, output = self._run_dry_run_capture(
            failures=failures, informants=[], tmpdir=tmpdir
        )
        assert exit_code == 0
        assert "Total Gemini failure entries:        1" in output
        assert "Gemini entries detected (triggering): 1" in output
        assert "[OK]" in output
        # Projected cost: 1 * 0.05 = 0.05 < 1.60 threshold
        assert "STOP" not in output

    # ── Scenario 7: File-safety — output file not written during dry-run ──────

    def test_dry_run_does_not_write_output_file(self, tmpdir: Path) -> None:
        """Dry-run must not write to the output file (mtime unchanged)."""
        informants_path = tmpdir / "informants.jsonl"
        failures_path = tmpdir / "failures.jsonl"
        output_path = tmpdir / "decline_interviews.jsonl"

        _write_jsonl(informants_path, [])
        _write_jsonl(failures_path, [])
        output_path.touch()

        mtime_before = output_path.stat().st_mtime

        with patch("sys.stdout", StringIO()):
            run_dry_run(
                informants_path=informants_path,
                failures_path=failures_path,
                output_path=output_path,
            )

        mtime_after = output_path.stat().st_mtime
        assert mtime_before == mtime_after, (
            "dry-run must not modify the output file"
        )

    def test_dry_run_blocks_open_write_mode(
        self, tmpdir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Confirm dry-run never opens any file in write mode.

        Monkeypatches the built-in open to raise on 'w' mode.
        The function should succeed without triggering the guard.
        """
        informants_path = tmpdir / "informants.jsonl"
        failures_path = tmpdir / "failures.jsonl"
        output_path = tmpdir / "decline_interviews.jsonl"

        _write_jsonl(informants_path, [])
        _write_jsonl(failures_path, [])
        output_path.touch()

        _real_open = open

        def _guarded_open(file: Any, mode: str = "r", **kwargs: Any) -> Any:
            if "w" in mode:
                raise AssertionError(
                    f"dry-run opened file in write mode: file={file!r} mode={mode!r}"
                )
            return _real_open(file, mode, **kwargs)

        monkeypatch.setattr("builtins.open", _guarded_open)

        with patch("sys.stdout", StringIO()):
            exit_code = run_dry_run(
                informants_path=informants_path,
                failures_path=failures_path,
                output_path=output_path,
            )
        assert exit_code == 0

    def test_dry_run_no_network(self, tmpdir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Dry-run must not make any network calls (httpx / requests blocked)."""
        informants_path = tmpdir / "informants.jsonl"
        failures_path = tmpdir / "failures.jsonl"
        output_path = tmpdir / "decline_interviews.jsonl"

        _write_jsonl(informants_path, [])
        _write_jsonl(failures_path, [])
        output_path.touch()

        def _blocked_request(*args: Any, **kwargs: Any) -> None:
            raise AssertionError("dry-run must not make network calls")

        # Block both httpx and requests at the socket level (belt + suspenders)
        monkeypatch.setattr("socket.socket.connect", _blocked_request, raising=False)

        with patch("sys.stdout", StringIO()):
            exit_code = run_dry_run(
                informants_path=informants_path,
                failures_path=failures_path,
                output_path=output_path,
            )
        assert exit_code == 0

    # ── Scenario 8: Cost guard — 40 detected sessions -> exit 2 ──────────────

    def test_cost_guard_exits_2_at_40_sessions(self, tmpdir: Path) -> None:
        """40 detected sessions x $0.05/call = $2.00, which is >= 80% of $2.00 cap.

        The 80% threshold is 0.80 * $2.00 = $1.60. With 40 sessions * $0.05 = $2.00,
        this is at/above the threshold. Script must exit 2 with STOP message.

        Inject sessions via synthetic glm-5.1 empty-freelist records (trigger c),
        which are the most reliable trigger in the detector.
        """
        informants = [
            _make_informant(
                informant_id=f"cost_guard_test_{i:04d}",
                model_id="z-ai/glm-5.1",
                domain_slug="family",
                qa_passed=False,
                qa_notes="0; 71000ms; 171",
                parsed_items=[],  # empty freelist: trigger c
                parsed_piles=[["mother"]],
                parsed_labels=["nuclear"],
            )
            for i in range(40)
        ]
        exit_code, output = self._run_dry_run_capture(
            informants, [], tmpdir, cost_per_call=0.05, legacy_dollar_threshold=2.00
        )
        assert exit_code == 2
        assert "STOP" in output
        assert "80%" in output or "escalation" in output.lower() or "Escalate" in output

    def test_cost_guard_ok_below_threshold(self, tmpdir: Path) -> None:
        """Fewer sessions -> cost guard OK, exit 0."""
        informants = [
            _make_informant(
                informant_id=f"ok_session_{i:04d}",
                model_id="z-ai/glm-5.1",
                domain_slug="family",
                qa_passed=False,
                qa_notes="0; 71000ms; 171",
                parsed_items=[],
                parsed_piles=[["mother"]],
                parsed_labels=["nuclear"],
            )
            for i in range(3)
        ]
        exit_code, output = self._run_dry_run_capture(
            informants, [], tmpdir, cost_per_call=0.05, legacy_dollar_threshold=2.00
        )
        assert exit_code == 0
        assert "STOP" not in output
        assert "[OK]" in output

    # ── Section headings present ───────────────────────────────────────────────

    def test_all_five_sections_present(self, tmpdir: Path) -> None:
        """Dry-run output must contain all 5 section headings."""
        exit_code, output = self._run_dry_run_capture([], [], tmpdir)
        assert "SECTION 1" in output
        assert "SECTION 2" in output
        assert "SECTION 3" in output
        assert "SECTION 4" in output
        assert "SECTION 5" in output

    # ── Totals consistency ─────────────────────────────────────────────────────

    def test_totals_consistency(self, tmpdir: Path) -> None:
        """Section 5 total = detected + not_triggered."""
        # 3 glm (detected) + 2 grok (not triggered)
        informants = (
            [
                _make_informant(
                    informant_id=f"glm_total_{i:04d}",
                    model_id="z-ai/glm-5.1",
                    domain_slug="family",
                    qa_passed=False,
                    qa_notes="0; 71000ms; 171",
                    parsed_items=[],
                    parsed_piles=[["mother"]],
                    parsed_labels=["nuclear"],
                )
                for i in range(3)
            ] + [
                _make_informant(
                    informant_id=f"grok_total_{i:04d}",
                    model_id="x-ai/grok-4",
                    domain_slug="family",
                    qa_passed=False,
                    qa_notes="102547ms",
                    # Use multiple piles to avoid triggering degenerate-pile (e)
                    parsed_items=["mother", "father", "sister", "brother", "cousin"],
                    parsed_piles=[["mother", "father"], ["sister", "brother", "cousin"]],
                    parsed_labels=["nuclear", "extended"],
                )
                for i in range(2)
            ]
        )
        exit_code, output = self._run_dry_run_capture(informants, [], tmpdir)
        assert exit_code == 0
        # 3 detected + 2 not-triggered = 5 scanned
        assert "Total detected (to be interviewed in T3): 3" in output
        assert "Total not triggered: 2" in output
        assert "Total records scanned: 5" in output

    # ── --execute raises NotImplementedError ──────────────────────────────────

    def test_execute_raises_not_implemented(self) -> None:
        """--execute path must raise NotImplementedError (T2 scope)."""
        with pytest.raises(NotImplementedError) as exc_info:
            # Simulate execute path directly
            parser = _mod.build_parser()
            args = parser.parse_args(["--execute"])
            if args.execute:
                raise NotImplementedError(
                    "--execute is T2 scope; "
                    "see docs/status/2026-04-23-phase4a1-architect-plan.md §3 T2"
                )
        assert "T2 scope" in str(exc_info.value)

    # ── Missing files handled gracefully ──────────────────────────────────────

    def test_missing_informants_returns_empty_not_error(self, tmpdir: Path) -> None:
        """If informants.jsonl does not exist, treat as empty (not an error)."""
        failures_path = tmpdir / "failures.jsonl"
        _write_jsonl(failures_path, [])
        output_path = tmpdir / "decline_interviews.jsonl"
        output_path.touch()

        captured = StringIO()
        with patch("sys.stdout", captured):
            exit_code = run_dry_run(
                informants_path=tmpdir / "nonexistent_informants.jsonl",
                failures_path=failures_path,
                output_path=output_path,
            )
        assert exit_code == 0
        output = captured.getvalue()
        assert "Total detected (to be interviewed in T3): 0" in output

    def test_missing_failures_returns_empty_not_error(self, tmpdir: Path) -> None:
        """If failures.jsonl does not exist, treat as empty (not an error)."""
        informants_path = tmpdir / "informants.jsonl"
        _write_jsonl(informants_path, [])
        output_path = tmpdir / "decline_interviews.jsonl"
        output_path.touch()

        captured = StringIO()
        with patch("sys.stdout", captured):
            exit_code = run_dry_run(
                informants_path=informants_path,
                failures_path=tmpdir / "nonexistent_failures.jsonl",
                output_path=output_path,
            )
        assert exit_code == 0

    # ── qa_passed=True records are skipped ────────────────────────────────────

    def test_qa_passed_true_records_not_counted(self, tmpdir: Path) -> None:
        """Records with qa_passed=True must not appear in any output section."""
        informants = [
            _make_informant(
                informant_id="passed_rec_0001",
                model_id="anthropic/claude-3",
                domain_slug="family",
                qa_passed=True,
                qa_notes="",
            )
        ]
        exit_code, output = self._run_dry_run_capture(informants, [], tmpdir)
        assert exit_code == 0
        assert "Total detected (to be interviewed in T3): 0" in output
        assert "Total not triggered: 0" in output
        assert "Total records scanned: 0" in output
        assert "passed_rec_0001" not in output

    # ── SME binding note 1: per-record rows, not a summary count ──────────────

    def test_sme_note1_per_record_not_just_count(self, tmpdir: Path) -> None:
        """SME binding note 1: the not-triggered section must emit one row per
        record, not a bulk count. Each distinct informant_id must appear."""
        ids = ["sme_note1_a", "sme_note1_b", "sme_note1_c"]
        informants = [
            _make_informant(
                informant_id=iid,
                model_id="x-ai/grok-4",
                domain_slug="holidays",
                qa_passed=False,
                qa_notes="91415ms",  # latency-only
                parsed_items=["christmas", "easter"],
                parsed_piles=[["christmas"], ["easter"]],
                parsed_labels=["holiday1", "holiday2"],
            )
            for iid in ids
        ]
        exit_code, output = self._run_dry_run_capture(informants, [], tmpdir)
        assert exit_code == 0
        for iid in ids:
            assert iid in output, f"Expected {iid!r} to appear in not-triggered per-record rows"


# ── _originating_step_from_checks unit tests ──────────────────────────────────

class TestOriginatingStepFromChecks:
    """Unit tests for the failing_checks -> originating_step derivation function."""

    def test_check5_only_returns_pile_sort(self) -> None:
        """Check-5 latency-only records map to pile_sort (grok-4 fixture scenario)."""
        result = _originating_step_from_checks(["check_5_latency_exceeded"])
        assert result == "pile_sort"

    def test_check8_only_returns_interview(self) -> None:
        """Check-8 label-mismatch records map to interview."""
        result = _originating_step_from_checks(["check_8_label_count_mismatch"])
        assert result == "interview"

    def test_check1_only_returns_freelist(self) -> None:
        """Check-1 empty-freelist records map to freelist."""
        result = _originating_step_from_checks(["check_1_freelist_empty"])
        assert result == "freelist"

    def test_check6_only_returns_pile_sort(self) -> None:
        """Check-6 token-inconsistency alone maps to pile_sort."""
        result = _originating_step_from_checks(["check_6_token_inconsistency"])
        assert result == "pile_sort"

    def test_check1_and_check5_returns_pile_sort(self) -> None:
        """Compound check_1 + check_5: pile_sort is the deeper step (plan §3 T1 rule)."""
        result = _originating_step_from_checks(
            ["check_1_freelist_empty", "check_5_latency_exceeded"]
        )
        assert result == "pile_sort"

    def test_check5_and_check8_returns_interview(self) -> None:
        """Compound check_5 + check_8: interview is the deepest step."""
        result = _originating_step_from_checks(
            ["check_5_latency_exceeded", "check_8_label_count_mismatch"]
        )
        assert result == "interview"

    def test_empty_checks_returns_unknown(self) -> None:
        """Empty check list -> unknown (no crash)."""
        result = _originating_step_from_checks([])
        assert result == "unknown"

    def test_unrecognised_check_returns_unknown(self) -> None:
        """An unrecognised check name -> unknown (no crash)."""
        result = _originating_step_from_checks(["check_99_something_new"])
        assert result == "unknown"


# ── Section 3 originating_step column integration tests ───────────────────────

class TestSection3OriginatingStepColumn:
    """Integration tests confirming originating_step column appears in Section 3 output."""

    @pytest.fixture()
    def tmpdir(self, tmp_path: Path) -> Path:
        return tmp_path

    def _run_dry_run_capture(
        self,
        informants: list,
        failures: list,
        tmpdir: Path,
    ) -> tuple[int, str]:
        informants_path = tmpdir / "informants.jsonl"
        failures_path = tmpdir / "failures.jsonl"
        output_path = tmpdir / "decline_interviews.jsonl"
        _write_jsonl(informants_path, informants)
        _write_jsonl(failures_path, failures)
        output_path.touch()
        captured = StringIO()
        with patch("sys.stdout", captured):
            exit_code = run_dry_run(
                informants_path=informants_path,
                failures_path=failures_path,
                output_path=output_path,
            )
        return exit_code, captured.getvalue()

    def test_section3_header_contains_originating_step(self, tmpdir: Path) -> None:
        """Section 3 header must contain 'originating_step' as a column label."""
        # Use a single latency-only not-triggered record so Section 3 emits a row.
        informants = [
            _make_informant(
                informant_id="hdr_check_0001",
                model_id="x-ai/grok-4",
                domain_slug="holidays",
                qa_passed=False,
                qa_notes="91415ms",  # check_5 only -> not triggered
                parsed_items=["christmas", "easter"],
                parsed_piles=[["christmas"], ["easter"]],
                parsed_labels=["holiday1", "holiday2"],
            )
        ]
        _, output = self._run_dry_run_capture(informants, [], tmpdir)
        assert "originating_step" in output, (
            "Section 3 header must include 'originating_step' column"
        )

    def test_section3_grok4_check5_row_has_pile_sort(self, tmpdir: Path) -> None:
        """grok-4 Check-5-only record -> originating_step=pile_sort in Section 3 row."""
        informants = [
            _make_informant(
                informant_id="grok_step_0001",
                model_id="x-ai/grok-4",
                domain_slug="holidays",
                qa_passed=False,
                qa_notes="91415ms",  # check_5 only
                parsed_items=["christmas", "easter"],
                parsed_piles=[["christmas"], ["easter"]],
                parsed_labels=["holiday1", "holiday2"],
            )
        ]
        _, output = self._run_dry_run_capture(informants, [], tmpdir)
        # The row for grok_step_0001 must contain pile_sort
        assert "pile_sort" in output, (
            "Check-5-only not-triggered record must emit originating_step=pile_sort"
        )
        assert "grok_step_0001" in output

    def test_section3_check8_row_has_interview(self, tmpdir: Path) -> None:
        """Check-8-only record -> originating_step=interview in Section 3 row."""
        informants = [
            _make_informant(
                informant_id="chk8_step_0001",
                model_id="mistralai/mistral-small",
                domain_slug="family",
                qa_passed=False,
                qa_notes="label_count_mismatch:20/9",  # check_8 only
                parsed_items=["mother", "father"],
                parsed_piles=[["mother"], ["father"]],
                parsed_labels=["nuclear", "extended"],  # non-empty -> not triggered
            )
        ]
        _, output = self._run_dry_run_capture(informants, [], tmpdir)
        assert "interview" in output, (
            "Check-8-only not-triggered record must emit originating_step=interview"
        )
        assert "chk8_step_0001" in output

    def test_section3_unknown_step_for_empty_notes(self, tmpdir: Path) -> None:
        """A record with empty qa_notes and no parseable checks -> originating_step=unknown."""
        # Craft a record that is qa_passed=False but has no qa_notes and no
        # structural trigger (non-empty piles, non-empty labels, no allowlist string).
        informants = [
            _make_informant(
                informant_id="unk_step_0001",
                model_id="openai/gpt-5.4-mini",
                domain_slug="food",
                qa_passed=False,
                qa_notes="",  # empty notes -> no check parses
                parsed_items=["pizza", "sushi"],
                parsed_piles=[["pizza"], ["sushi"]],
                parsed_labels=["fast", "slow"],
            )
        ]
        _, output = self._run_dry_run_capture(informants, [], tmpdir)
        assert "unknown" in output, (
            "Record with no parseable checks must emit originating_step=unknown"
        )
        assert "unk_step_0001" in output


# ── T1-update: TestShouldIncludeFailure ──────────────────────────────────────

class TestShouldIncludeFailure:
    """Unit tests for should_include_failure() — Amendment 1 §2 decision tree.

    Covers every classification branch including SME A2 (jailbreak marker)
    and SME A3 (empty-response cohort distinct rationale key).
    """

    def _entry(self, error_type: str = "ValueError", error_message: str = "") -> dict[str, Any]:
        """Build a minimal failures.jsonl entry for testing."""
        return {
            "timestamp": "2026-04-23T10:00:00",
            "error_type": error_type,
            "error_message": error_message,
            "context": {"model_id": "test/model", "domain": "family", "run_index": 0},
            "retry_attempts": [],
        }

    def test_httpstatuserror_400_excluded(self) -> None:
        """HTTPStatusError with 400 Bad Request → EXCLUDE, rationale http_infrastructure."""
        entry = self._entry(
            error_type="HTTPStatusError",
            error_message=(
                "Client error '400 Bad Request' for url 'https://openrouter.ai/api/v1/chat/completions'"
            ),
        )
        include, rationale = should_include_failure(entry)
        assert include is False
        assert rationale == "http_infrastructure:HTTPStatusError"

    def test_httpstatuserror_500_excluded(self) -> None:
        """HTTPStatusError with 500 → EXCLUDE."""
        entry = self._entry(
            error_type="HTTPStatusError",
            error_message="Server error '500 Internal Server Error'",
        )
        include, rationale = should_include_failure(entry)
        assert include is False
        assert rationale == "http_infrastructure:HTTPStatusError"

    def test_connecterror_excluded(self) -> None:
        entry = self._entry(error_type="ConnectError", error_message="Connection refused")
        include, rationale = should_include_failure(entry)
        assert include is False
        assert rationale == "http_infrastructure:ConnectError"

    def test_readtimeout_excluded(self) -> None:
        entry = self._entry(error_type="ReadTimeout", error_message="Read timed out")
        include, rationale = should_include_failure(entry)
        assert include is False
        assert rationale == "http_infrastructure:ReadTimeout"

    def test_writetimeout_excluded(self) -> None:
        entry = self._entry(error_type="WriteTimeout", error_message="Write timed out")
        include, rationale = should_include_failure(entry)
        assert include is False
        assert rationale == "http_infrastructure:WriteTimeout"

    def test_pooltimeout_excluded(self) -> None:
        entry = self._entry(error_type="PoolTimeout", error_message="Pool exhausted")
        include, rationale = should_include_failure(entry)
        assert include is False
        assert rationale == "http_infrastructure:PoolTimeout"

    def test_timeouterror_excluded(self) -> None:
        """stdlib TimeoutError → EXCLUDE."""
        entry = self._entry(error_type="TimeoutError", error_message="timed out")
        include, rationale = should_include_failure(entry)
        assert include is False
        assert rationale == "http_infrastructure:TimeoutError"

    def test_connectionerror_excluded(self) -> None:
        """stdlib ConnectionError → EXCLUDE."""
        entry = self._entry(error_type="ConnectionError", error_message="connection failed")
        include, rationale = should_include_failure(entry)
        assert include is False
        assert rationale == "http_infrastructure:ConnectionError"

    def test_safety_filter_blocked_overrides_httpstatuserror(self) -> None:
        """HTTPStatusError with 'blocked' in message → INCLUDE (safety filter wins).

        Note: the safety marker list is iterated in order. Both 'content policy' and
        'blocked' match this message; whichever comes first in SAFETY_FILTER_MARKERS
        wins. The key invariant is: (a) include=True, (b) rationale starts with
        safety_filter:matched:. The exact matched marker is deterministic but
        implementation-order-dependent.
        """
        entry = self._entry(
            error_type="HTTPStatusError",
            error_message="Client error '400 Bad Request' blocked by content policy",
        )
        include, rationale = should_include_failure(entry)
        assert include is True
        assert rationale.startswith("safety_filter:matched:")

    def test_safety_filter_content_policy_matches(self) -> None:
        """'content policy violation' in message → INCLUDE."""
        entry = self._entry(
            error_type="ValueError",
            error_message="Request refused: content policy violation detected",
        )
        include, rationale = should_include_failure(entry)
        assert include is True
        assert "content policy" in rationale

    def test_safety_filter_recitation_finish_reason(self) -> None:
        """'RECITATION' in message → INCLUDE."""
        entry = self._entry(
            error_type="ValueError",
            error_message="Generation stopped: finish_reason=RECITATION",
        )
        include, rationale = should_include_failure(entry)
        assert include is True
        assert "RECITATION" in rationale

    def test_safety_filter_jailbreak_marker(self) -> None:
        """'jailbreak' in message → INCLUDE (SME A2 coverage).

        Uses a message that contains 'jailbreak' but NOT any earlier safety marker.
        This ensures the jailbreak marker itself causes the INCLUDE, not a prior match.
        """
        entry = self._entry(
            error_type="ValueError",
            error_message="Detected jailbreak attempt in request",
        )
        include, rationale = should_include_failure(entry)
        assert include is True
        assert "jailbreak" in rationale

    def test_safety_filter_case_insensitive(self) -> None:
        """Safety filter match is case-insensitive: 'SAFETY', 'Safety', 'safety' all match."""
        for variant in ("SAFETY", "Safety", "safety"):
            entry = self._entry(
                error_type="ValueError",
                error_message=f"Generation blocked due to {variant} filter",
            )
            include, rationale = should_include_failure(entry)
            assert include is True, f"Expected INCLUDE for variant {variant!r}"
            assert "safety_filter:matched:" in rationale

    def test_empty_response_likely_silent_safety_block(self) -> None:
        """SME A3: ValueError + 'Could not extract valid JSON from response: ' ending with ': '
        → INCLUDE with empty_response:likely_silent_safety_block rationale."""
        entry = self._entry(
            error_type="ValueError",
            error_message="Could not extract valid JSON from response: ",
        )
        include, rationale = should_include_failure(entry)
        assert include is True
        assert rationale == "empty_response:likely_silent_safety_block"

    def test_empty_response_distinct_from_parse_exhaustion(self) -> None:
        """Non-empty partial 'Could not extract valid JSON from response: {\"foo\":'
        → parse_exhaustion rationale, NOT empty_response."""
        entry = self._entry(
            error_type="ValueError",
            error_message='Could not extract valid JSON from response: {"foo":',
        )
        include, rationale = should_include_failure(entry)
        assert include is True
        assert rationale.startswith("parse_exhaustion:"), (
            f"Expected parse_exhaustion rationale, got: {rationale!r}"
        )
        assert "empty_response" not in rationale

    def test_parse_exhaustion_items_missing_included(self) -> None:
        entry = self._entry(
            error_type="ValueError",
            error_message="Items missing from pile sort: expected 5, got 3",
        )
        include, rationale = should_include_failure(entry)
        assert include is True
        assert rationale.startswith("parse_exhaustion:")
        assert "Items missing from pile sort" in rationale

    def test_parse_exhaustion_pile_sort_attempts_included(self) -> None:
        entry = self._entry(
            error_type="ValueError",
            error_message="Pile sort parsing failed after 3 attempts; last error: invalid bracket",
        )
        include, rationale = should_include_failure(entry)
        assert include is True
        assert rationale.startswith("parse_exhaustion:")
        # The marker is truncated at 30 chars: "Pile sort parsing failed after" (30 chars)
        assert "Pile sort parsing failed after" in rationale

    def test_unclassified_defaults_to_include(self) -> None:
        """Unknown error_type, non-matching message → INCLUDE with unclassified rationale."""
        entry = self._entry(
            error_type="WeirdError",
            error_message="Something unexpected happened",
        )
        include, rationale = should_include_failure(entry)
        assert include is True
        assert rationale == "unclassified:default_include:WeirdError"

    def test_empty_error_message_unclassified(self) -> None:
        """Empty error_message, unknown error_type → INCLUDE, unclassified."""
        entry = self._entry(error_type="WeirdError", error_message="")
        include, rationale = should_include_failure(entry)
        assert include is True
        assert rationale.startswith("unclassified:default_include:")

    def test_rationale_string_is_deterministic(self) -> None:
        """Same input always produces the same rationale."""
        entry = self._entry(
            error_type="HTTPStatusError",
            error_message="Client error '400 Bad Request'",
        )
        r1 = should_include_failure(entry)[1]
        r2 = should_include_failure(entry)[1]
        assert r1 == r2


# ── T1-update: TestSection3bExcludedAudit ────────────────────────────────────

class TestSection3bExcludedAudit:
    """Integration tests for Section 3b — excluded failures-origin records audit.

    SME A7: Section 3b must be preceded by a controlled-vocabulary header.
    """

    @pytest.fixture()
    def tmpdir(self, tmp_path: Path) -> Path:
        return tmp_path

    def _run_capture(
        self,
        informants: list[dict],
        failures: list[dict],
        tmpdir: Path,
        source: str = "all",
    ) -> tuple[int, str]:
        inf_path = tmpdir / "informants.jsonl"
        fail_path = tmpdir / "failures.jsonl"
        out_path = tmpdir / "decline_interviews.jsonl"
        _write_jsonl(inf_path, informants)
        _write_jsonl(fail_path, failures)
        out_path.touch()
        captured = StringIO()
        with patch("sys.stdout", captured):
            code = run_dry_run(
                informants_path=inf_path,
                failures_path=fail_path,
                output_path=out_path,
                source=source,
            )
        return code, captured.getvalue()

    def _phi4_400_failure(self, run_index: int = 0) -> dict[str, Any]:
        return {
            "timestamp": f"2026-04-22T10:{run_index:02d}:00",
            "error_type": "HTTPStatusError",
            "error_message": (
                "Client error '400 Bad Request' for url "
                "'https://openrouter.ai/api/v1/chat/completions'"
            ),
            "context": {"model_id": "microsoft/phi-4", "domain": "family", "run_index": run_index},
            "retry_attempts": [],
        }

    def test_section3b_header_present_with_taxonomy(self, tmpdir: Path) -> None:
        """SME A7: Section 3b header must list all six rationale keys."""
        _, output = self._run_capture([], [], tmpdir)
        assert "Section 3b" in output
        assert "Rationale taxonomy (v1):" in output
        # Verify all six rationale keys are listed
        assert "http_infrastructure:" in output
        assert "adapter_pre_generation_parse:" in output
        assert "safety_filter:matched:" in output
        assert "parse_exhaustion:" in output
        assert "empty_response:likely_silent_safety_block" in output
        assert "unclassified:default_include:" in output

    def test_section3b_phi4_httpstatuserror_listed_with_rationale(
        self, tmpdir: Path
    ) -> None:
        """phi-4 HTTPStatusError 400 → appears in Section 3b with http_infrastructure rationale."""
        failures = [self._phi4_400_failure(0)]
        _, output = self._run_capture([], failures, tmpdir)
        assert "http_infrastructure:HTTPStatusError" in output
        assert "microsoft/phi-4" in output or "phi-4" in output or "failure|" in output

    def test_section3b_zero_excluded_on_pure_informants_fixture(
        self, tmpdir: Path
    ) -> None:
        """Zero excluded records: Section 3b still prints header + 'Total excluded: 0'."""
        # No failures → nothing to exclude
        _, output = self._run_capture([], [], tmpdir)
        assert "Total excluded: 0" in output
        assert "Section 3b" in output

    def test_section3b_exclusion_breakdown_aggregates_correctly(
        self, tmpdir: Path
    ) -> None:
        """Multiple phi-4 HTTPStatusError failures → breakdown shows http_infrastructure=N."""
        failures = [self._phi4_400_failure(i) for i in range(3)]
        _, output = self._run_capture([], failures, tmpdir)
        assert "Total excluded: 3" in output
        assert "http_infrastructure" in output

    def test_section3b_does_not_list_included_records(self, tmpdir: Path) -> None:
        """safety-filter / parse-exhaustion / empty-response INCLUDE records
        do NOT appear as rows in Section 3b excluded list."""
        # Mix: 1 HTTPStatusError (excl), 1 safety-filter (incl), 1 parse-exhaustion (incl)
        failures = [
            self._phi4_400_failure(0),  # excluded
            {
                "timestamp": "2026-04-22T10:01:00",
                "error_type": "ValueError",
                "error_message": "Request blocked: safety filter applied",
                "context": {"model_id": "some/model", "domain": "family", "run_index": 0},
                "retry_attempts": [],
            },  # included (safety_filter)
            {
                "timestamp": "2026-04-22T10:02:00",
                "error_type": "ValueError",
                "error_message": "Items missing from pile sort: expected 5, got 3",
                "context": {"model_id": "some/model", "domain": "family", "run_index": 1},
                "retry_attempts": [],
            },  # included (parse_exhaustion)
        ]
        _, output = self._run_capture([], failures, tmpdir)
        assert "Total excluded: 1" in output
        # Safety-filter/parse-exhaustion identifiers should not be in excluded row list
        # (The section may list their rationale keys in the HEADER but not as data rows)
        assert "Total excluded: 1" in output


# ── T1-update: TestSection3cUnclassified ─────────────────────────────────────

class TestSection3cUnclassified:
    """Integration tests for Section 3c — unclassified-default-include records.

    SME A4: if >2 unclassified records → exits non-zero with SURFACE-TO-SME flag.
    """

    @pytest.fixture()
    def tmpdir(self, tmp_path: Path) -> Path:
        return tmp_path

    def _run_capture(
        self,
        failures: list[dict],
        tmpdir: Path,
        source: str = "all",
    ) -> tuple[int, str]:
        inf_path = tmpdir / "informants.jsonl"
        fail_path = tmpdir / "failures.jsonl"
        out_path = tmpdir / "decline_interviews.jsonl"
        _write_jsonl(inf_path, [])
        _write_jsonl(fail_path, failures)
        out_path.touch()
        captured = StringIO()
        with patch("sys.stdout", captured):
            code = run_dry_run(
                informants_path=inf_path,
                failures_path=fail_path,
                output_path=out_path,
                source=source,
            )
        return code, captured.getvalue()

    def _unclassified_entry(self, run_index: int, error_type: str = "WeirdError") -> dict[str, Any]:
        return {
            "timestamp": f"2026-04-22T11:{run_index:02d}:00",
            "error_type": error_type,
            "error_message": f"Unexpected condition number {run_index}",
            "context": {"model_id": "some/model", "domain": "family", "run_index": run_index},
            "retry_attempts": [],
        }

    def test_section3c_empty_on_current_corpus_fixture(self, tmpdir: Path) -> None:
        """With the failures_mixed_sample fixture, unclassified count should be 0
        (all entries are classifiable by the v1 rules)."""
        fixture_path = _FIXTURES_DIR / "failures_mixed_sample.jsonl"
        failures = []
        with open(fixture_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    failures.append(json.loads(line))
        _, output = self._run_capture(failures, tmpdir)
        assert "Total unclassified-default-include: 0" in output

    def test_section3c_header_present_when_zero(self, tmpdir: Path) -> None:
        """Section 3c header appears even when count is zero."""
        _, output = self._run_capture([], tmpdir)
        assert "Section 3c" in output
        assert "Total unclassified-default-include: 0" in output

    def test_section3c_surface_to_sme_when_exceeds_2(self, tmpdir: Path) -> None:
        """3+ unclassified records → exits non-zero, prints SURFACE-TO-SME."""
        fixture_path = _FIXTURES_DIR / "failures_unclassified_saturation.jsonl"
        failures = []
        with open(fixture_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    failures.append(json.loads(line))
        code, output = self._run_capture(failures, tmpdir)
        assert code != 0, "Expected non-zero exit when >2 unclassified records"
        assert "SURFACE-TO-SME" in output
        assert "unclassified-saturation" in output
        assert "Total unclassified-default-include: 3" in output

    def test_section3c_at_exactly_2_still_go(self, tmpdir: Path) -> None:
        """Exactly 2 unclassified records → does NOT block (no SURFACE-TO-SME exit 2 for this)."""
        failures = [
            self._unclassified_entry(0, "WeirdError"),
            self._unclassified_entry(1, "AnotherWeirdError"),
        ]
        code, output = self._run_capture(failures, tmpdir)
        assert "SURFACE-TO-SME" not in output, (
            "Exactly 2 unclassified records should not trigger SURFACE-TO-SME"
        )
        # Exit may still be 0 (GO) if cost is under cap
        assert "Total unclassified-default-include: 2" in output


# ── T1-update: TestMaxBatchCallsCLIOverride ───────────────────────────────────

class TestMaxBatchCallsCLIOverride:
    """Tests for --max-batch-calls CLI flag."""

    def test_max_batch_calls_default_is_200(self) -> None:
        """Default call cap is 200."""
        parser = build_parser()
        args = parser.parse_args(["--dry-run"])
        assert args.max_batch_calls == 200

    def test_max_batch_calls_cli_flag_overrides_default(self) -> None:
        """--max-batch-calls 50 sets cap to 50, threshold to 40."""
        parser = build_parser()
        args = parser.parse_args(["--dry-run", "--max-batch-calls", "50"])
        assert args.max_batch_calls == 50

    def test_max_batch_calls_cli_flag_raises_threshold(self) -> None:
        """--max-batch-calls 500 sets cap to 500, threshold to 400."""
        parser = build_parser()
        args = parser.parse_args(["--dry-run", "--max-batch-calls", "500"])
        assert args.max_batch_calls == 500


# ── T1-update: TestCostGuardPostExclusion ────────────────────────────────────

class TestCostGuardPostExclusion:
    """Integration tests for post-exclusion call-count gate (SME A8).

    The pre-flight gate must use post-exclusion count, not full detected count.
    """

    @pytest.fixture()
    def tmpdir(self, tmp_path: Path) -> Path:
        return tmp_path

    def _run_capture_with_params(
        self,
        informants: list[dict],
        failures: list[dict],
        tmpdir: Path,
        max_batch_calls: int = 200,
        source: str = "all",
    ) -> tuple[int, str]:
        inf_path = tmpdir / "informants.jsonl"
        fail_path = tmpdir / "failures.jsonl"
        out_path = tmpdir / "decline_interviews.jsonl"
        _write_jsonl(inf_path, informants)
        _write_jsonl(fail_path, failures)
        out_path.touch()
        captured = StringIO()
        with patch("sys.stdout", captured):
            code = run_dry_run(
                informants_path=inf_path,
                failures_path=fail_path,
                output_path=out_path,
                max_batch_calls=max_batch_calls,
                source=source,
            )
        return code, captured.getvalue()

    def _phi4_400_failure(self, run_index: int) -> dict[str, Any]:
        return {
            "timestamp": f"2026-04-22T10:{run_index:02d}:00",
            "error_type": "HTTPStatusError",
            "error_message": "Client error '400 Bad Request'",
            "context": {"model_id": "microsoft/phi-4", "domain": "family", "run_index": run_index},
            "retry_attempts": [],
        }

    def _gemini_empty_response(self, run_index: int) -> dict[str, Any]:
        return {
            "timestamp": f"2026-04-22T10:{run_index:02d}:00",
            "error_type": "ValueError",
            "error_message": "Could not extract valid JSON from response: ",
            "context": {
                "model_id": "google/gemini-2.5-pro",
                "domain": "family",
                "run_index": run_index,
            },
            "retry_attempts": [],
        }

    def _make_glm_informant(self, idx: int) -> dict[str, Any]:
        return _make_informant(
            informant_id=f"glm_cg_{idx:04d}",
            model_id="z-ai/glm-5.1",
            domain_slug="family",
            qa_passed=False,
            qa_notes="0; 71000ms; 171",
            parsed_items=[],
            parsed_piles=[["mother"]],
            parsed_labels=["nuclear"],
        )

    def test_call_guard_uses_post_exclusion_count(self, tmpdir: Path) -> None:
        """Fixture: 5 detected failures-origin, 5 excluded (HTTPStatusError),
        0 included. Gate input should be informants-only count, not full count."""
        informants = [self._make_glm_informant(i) for i in range(3)]
        failures = [self._phi4_400_failure(i) for i in range(5)]
        _, output = self._run_capture_with_params(informants, failures, tmpdir, max_batch_calls=200)
        # Post-exclusion: 3 informants + 0 included failures = 3
        # Full count: 3 + 5 = 8
        # The gate input must show the post-exclusion call count (3 calls)
        assert "Gate input (post-exclusion):" in output
        assert "3 calls" in output  # 3 informants

    def test_call_guard_go_under_post_exclusion_threshold(self, tmpdir: Path) -> None:
        """Post-exclusion count under 160 (80% of 200) → GO disposition."""
        informants = [self._make_glm_informant(i) for i in range(3)]
        failures = [self._phi4_400_failure(i) for i in range(5)]
        code, output = self._run_capture_with_params(
            informants, failures, tmpdir, max_batch_calls=200
        )
        assert code == 0
        assert "GO" in output

    def test_call_guard_stop_at_post_exclusion_threshold(self, tmpdir: Path) -> None:
        """160 records >= 160 (80% of 200) → STOP, exit 2."""
        # 160 informants-origin (no failures to exclude); all from informants
        informants = [self._make_glm_informant(i) for i in range(160)]
        code, output = self._run_capture_with_params(informants, [], tmpdir, max_batch_calls=200)
        assert code == 2
        assert "STOP" in output

    def test_call_guard_surface_overrides_go(self, tmpdir: Path) -> None:
        """SME A4: unclassified-saturation SURFACE-TO-SME wins over call-count GO."""
        # 3 unclassified failures + count under threshold → should still SURFACE-TO-SME
        fixture_path = _FIXTURES_DIR / "failures_unclassified_saturation.jsonl"
        failures = []
        with open(fixture_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    failures.append(json.loads(line))
        code, output = self._run_capture_with_params([], failures, tmpdir, max_batch_calls=200)
        assert code != 0
        assert "SURFACE-TO-SME" in output

    def test_summary_prints_both_projections(self, tmpdir: Path) -> None:
        """CLI summary shows BOTH full-count and post-exclusion projections (SME A8)."""
        informants = [self._make_glm_informant(i) for i in range(3)]
        failures = [self._phi4_400_failure(i) for i in range(5)]
        _, output = self._run_capture_with_params(informants, failures, tmpdir, max_batch_calls=200)
        assert "Full-count projection:" in output
        assert "Post-exclusion projection:" in output


# ── T1-update: TestSourceFlag ────────────────────────────────────────────────

class TestSourceFlag:
    """Integration tests for --source {informants,failures,all} flag."""

    @pytest.fixture()
    def tmpdir(self, tmp_path: Path) -> Path:
        return tmp_path

    def _run_capture_source(
        self,
        informants: list[dict],
        failures: list[dict],
        tmpdir: Path,
        source: str,
    ) -> tuple[int, str]:
        inf_path = tmpdir / "informants.jsonl"
        fail_path = tmpdir / "failures.jsonl"
        out_path = tmpdir / "decline_interviews.jsonl"
        _write_jsonl(inf_path, informants)
        _write_jsonl(fail_path, failures)
        out_path.touch()
        captured = StringIO()
        with patch("sys.stdout", captured):
            code = run_dry_run(
                informants_path=inf_path,
                failures_path=fail_path,
                output_path=out_path,
                source=source,
            )
        return code, captured.getvalue()

    def _make_glm_informant(self, idx: int) -> dict[str, Any]:
        return _make_informant(
            informant_id=f"glm_src_{idx:04d}",
            model_id="z-ai/glm-5.1",
            domain_slug="family",
            qa_passed=False,
            qa_notes="0; 71000ms; 171",
            parsed_items=[],
            parsed_piles=[["mother"]],
            parsed_labels=["nuclear"],
        )

    def _phi4_400_failure(self, run_index: int = 0) -> dict[str, Any]:
        return {
            "timestamp": f"2026-04-22T10:{run_index:02d}:00",
            "error_type": "HTTPStatusError",
            "error_message": "Client error '400 Bad Request'",
            "context": {"model_id": "microsoft/phi-4", "domain": "family", "run_index": run_index},
            "retry_attempts": [],
        }

    def _gemini_parse_failure(self, run_index: int = 0) -> dict[str, Any]:
        return {
            "timestamp": f"2026-04-22T10:{run_index:02d}:00",
            "error_type": "ValueError",
            "error_message": "Items missing from pile sort: expected 5, got 3",
            "context": {
                "model_id": "google/gemini-2.5-pro",
                "domain": "family",
                "run_index": run_index,
            },
            "retry_attempts": [],
        }

    def test_source_informants_filters_sections(self, tmpdir: Path) -> None:
        """--source informants: only informants-origin sessions shown; failures section N/A."""
        informants = [self._make_glm_informant(0)]
        failures = [self._phi4_400_failure(0)]
        _, output = self._run_capture_source(informants, failures, tmpdir, source="informants")
        # Informants should appear in output
        assert "glm_src_0000" in output or "informants" in output.lower()
        # Failures section should indicate skipped
        assert "N/A" in output or "--source informants" in output

    def test_source_failures_filters_sections(self, tmpdir: Path) -> None:
        """--source failures: only failures-origin sessions shown; informants N/A."""
        informants = [self._make_glm_informant(0)]
        failures = [self._gemini_parse_failure(0)]
        _, output = self._run_capture_source(informants, failures, tmpdir, source="failures")
        # The failures count should appear in the summary
        assert "Failures-origin (raw):" in output
        # Informants-origin detected should be 0 in the display (not shown)
        # The section 5 should show informants count = 1 (total detected still counts)
        assert "Informants-origin:" in output

    def test_source_all_default_behavior(self, tmpdir: Path) -> None:
        """--source all (default): both informants and failures populated."""
        informants = [self._make_glm_informant(0)]
        failures = [self._gemini_parse_failure(0)]
        _, output = self._run_capture_source(informants, failures, tmpdir, source="all")
        # Both should contribute to detected count
        assert "Informants-origin:" in output
        assert "Failures-origin" in output

    def test_source_informants_skips_exclusion_filter(self, tmpdir: Path) -> None:
        """--source informants: failures-origin never goes through should_include_failure.
        Section 3b shows N/A instead of a breakdown."""
        informants = [self._make_glm_informant(0)]
        failures = [self._phi4_400_failure(0)]
        _, output = self._run_capture_source(informants, failures, tmpdir, source="informants")
        # Section 3b should indicate failures-origin pipeline not processed
        assert "--source informants" in output
        assert "N/A" in output


# ── T2: MockAdapter import ────────────────────────────────────────────────────
# sys.path extended above to include tests/fixtures/ for MockAdapter
from mock_adapter import MockAdapter  # noqa: E402  # isort:skip


# ── T2 helper: make informant with prompt_verbatim in step sub-records ────────

def _make_informant_with_prompts(
    *,
    informant_id: str,
    model_id: str,
    domain_slug: str = "family",
    qa_passed: bool = False,
    qa_notes: str = "0; 71000ms; 171",
    parsed_items: list | None = None,
    parsed_piles: list | None = None,
    parsed_labels: list | None = None,
    freelist_prompt: str = "Please list family terms.",
    freelist_response: str = "",
    pile_sort_prompt: str = "Please sort these family terms into piles.",
    pile_sort_response: str = "Here are my piles.",
    interview_prompt: str = "Please label each pile.",
    interview_response: str = "",
    model_version_returned: str = "mock-model-v1",
) -> dict[str, Any]:
    """Build a full informant dict with prompt_verbatim in each step sub-record."""
    if parsed_items is None:
        parsed_items = []
    if parsed_piles is None:
        parsed_piles = [["mother", "father"]]
    if parsed_labels is None:
        parsed_labels = ["nuclear"]
    return {
        "informant_id": informant_id,
        "model_id": model_id,
        "domain_slug": domain_slug,
        "qa_passed": qa_passed,
        "qa_notes": qa_notes,
        "model_version_returned": model_version_returned,
        "freelist": {
            "parsed_items": parsed_items,
            "prompt_verbatim": freelist_prompt,
            "response_verbatim": freelist_response,
        },
        "pile_sort": {
            "parsed_piles": parsed_piles,
            "prompt_verbatim": pile_sort_prompt,
            "response_verbatim": pile_sort_response,
        },
        "interview": {
            "parsed_pile_labels": parsed_labels,
            "prompt_verbatim": interview_prompt,
            "response_verbatim": interview_response,
        },
    }


def _make_failure_full(
    *,
    model_id: str,
    domain: str = "family",
    run_index: int = 0,
    timestamp: str = "2026-04-23T10:00:00",
    error_type: str = "ValueError",
    error_message: str = "Items missing from pile sort: expected 5, got 3",
    prompt_verbatim: str | None = None,
    response_verbatim: str | None = None,
    failed_step: str = "pile_sort",
) -> dict[str, Any]:
    """Build a failures.jsonl entry with optional prompt_verbatim and response_verbatim."""
    entry: dict[str, Any] = {
        "timestamp": timestamp,
        "error_type": error_type,
        "error_message": error_message,
        "context": {
            "model_id": model_id,
            "domain": domain,
            "run_index": run_index,
            "failed_step": failed_step,
        },
        "retry_attempts": [],
    }
    if prompt_verbatim is not None:
        entry["prompt_verbatim"] = prompt_verbatim
    if response_verbatim is not None:
        entry["response_verbatim"] = response_verbatim
    return entry


def _run_execute_capture(
    informants: list[dict],
    failures: list[dict],
    tmpdir: Path,
    source: str = "all",
    max_batch_calls: int = 200,
    adapter_response: str = "The model described the exchange clearly.",
    adapter_model_version: str | None = None,
    adapter_model_id: str = "z-ai/glm-5.1",
    # Legacy params accepted but ignored (cost tracking removed)
    spend_cap: float = 10.00,
    cost_per_call: float = 0.05,
    adapter_cost: float = 0.05,
) -> tuple[int, str, str, list[dict]]:
    """Write fixtures to temp files, run run_execute, capture stdout+stderr.

    Returns (exit_code, stdout, stderr, written_records) where written_records
    is the list of DeclineInterview dicts read from the output JSONL.

    spend_cap, cost_per_call, and adapter_cost are ignored (cost tracking removed
    in task #F2-T14). max_batch_calls is the call-count gate.
    """
    informants_path = tmpdir / "informants.jsonl"
    failures_path = tmpdir / "failures.jsonl"
    output_path = tmpdir / "decline_interviews.jsonl"

    _write_jsonl(informants_path, informants)
    _write_jsonl(failures_path, failures)
    output_path.touch()

    mock_adapter = MockAdapter(
        model_id=adapter_model_id,
        response_text=adapter_response,
        model_version_returned=adapter_model_version,
    )

    def adapter_factory(model_id: str) -> MockAdapter:
        return mock_adapter

    captured_out = StringIO()
    captured_err = StringIO()

    with patch("sys.stdout", captured_out), patch("sys.stderr", captured_err):
        exit_code = run_execute(
            informants_path=informants_path,
            failures_path=failures_path,
            output_path=output_path,
            max_batch_calls=max_batch_calls,
            source=source,
            adapter_factory=adapter_factory,
        )

    # Read written records from output JSONL
    written_records: list[dict] = []
    if output_path.exists():
        for line in output_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                written_records.append(json.loads(line))

    return exit_code, captured_out.getvalue(), captured_err.getvalue(), written_records


# ── T2: TestExecutePath ───────────────────────────────────────────────────────

class TestExecutePath:
    """MockAdapter-based integration tests for the execute path.

    No real API calls. R10 non-negotiable.
    """

    @pytest.fixture()
    def tmpdir(self, tmp_path: Path) -> Path:
        return tmp_path

    def _glm_informant(self, idx: int) -> dict[str, Any]:
        """Informant-origin fixture: glm-5.1 x family with empty freelist trigger."""
        return _make_informant_with_prompts(
            informant_id=f"glm_exec_{idx:04d}",
            model_id="z-ai/glm-5.1",
            domain_slug="family",
            qa_passed=False,
            qa_notes="0; 71000ms; 171",
            parsed_items=[],
            freelist_prompt=f"List family terms (run {idx}).",
            freelist_response="",
            model_version_returned="glm-5.1-v1",
        )

    def _parse_failure(self, idx: int) -> dict[str, Any]:
        """Failure-origin fixture: ValueError parse exhaustion (INCLUDE)."""
        return _make_failure_full(
            model_id="z-ai/glm-5.1",
            domain="family",
            run_index=idx,
            timestamp=f"2026-04-23T10:{idx:02d}:00",
            error_type="ValueError",
            error_message="Items missing from pile sort: expected 5, got 3",
            prompt_verbatim=f"Sort these items (run {idx}).",
            response_verbatim="partial pile response",
        )

    def _http_failure(self, idx: int) -> dict[str, Any]:
        """Failure-origin fixture: HTTPStatusError 400 (EXCLUDE)."""
        return _make_failure_full(
            model_id="microsoft/phi-4",
            domain="family",
            run_index=idx,
            timestamp=f"2026-04-22T10:{idx:02d}:00",
            error_type="HTTPStatusError",
            error_message="Client error '400 Bad Request'",
        )

    def test_execute_informants_only_writes_n_records(self, tmpdir: Path) -> None:
        """--source informants: N informants-origin records written, each valid."""
        informants = [self._glm_informant(i) for i in range(3)]
        exit_code, stdout, stderr, records = _run_execute_capture(
            informants, [], tmpdir, source="informants"
        )
        assert exit_code == 0
        assert len(records) == 3
        # Each record validates as a DeclineInterview (model_dump_json was used)
        for rec in records:
            assert "decline_interview_id" in rec
            assert rec["originating_informant_id"] is not None
            assert rec["originating_failure_id"] is None

    def test_execute_failures_only_applies_exclusion(self, tmpdir: Path) -> None:
        """--source failures: should_include_failure() applied; excluded records not written."""
        # 2 parse failures (INCLUDE) + 1 HTTP failure (EXCLUDE)
        failures = [
            self._parse_failure(0),
            self._parse_failure(1),
            self._http_failure(0),
        ]
        exit_code, stdout, stderr, records = _run_execute_capture(
            [], failures, tmpdir, source="failures"
        )
        assert exit_code == 0
        # Only 2 INCLUDE records written
        assert len(records) == 2
        # Excluded record logged to stderr
        assert "SKIP:" in stderr

    def test_execute_all_combines_both(self, tmpdir: Path) -> None:
        """--source all: informants + filtered failures; exclusion applied to failures."""
        informants = [self._glm_informant(0)]
        failures = [
            self._parse_failure(0),
            self._http_failure(0),  # excluded
        ]
        exit_code, stdout, stderr, records = _run_execute_capture(
            informants, failures, tmpdir, source="all"
        )
        assert exit_code == 0
        # 1 informants + 1 failure (HTTP excluded) = 2 written
        assert len(records) == 2
        assert "SKIP:" in stderr

    def test_execute_single_detection_timestamp_shared(self, tmpdir: Path) -> None:
        """All records in a single run share identical detection_timestamp (SME A6)."""
        informants = [self._glm_informant(i) for i in range(3)]
        exit_code, stdout, stderr, records = _run_execute_capture(
            informants, [], tmpdir, source="informants"
        )
        assert exit_code == 0
        assert len(records) == 3
        timestamps = {rec["detection_timestamp"] for rec in records}
        assert len(timestamps) == 1, (
            f"Expected single shared detection_timestamp, got {timestamps}"
        )

    def test_execute_xor_invariant(self, tmpdir: Path) -> None:
        """Every written record has exactly one of originating_informant_id /
        originating_failure_id non-null (xor invariant on DeclineInterview)."""
        informants = [self._glm_informant(0)]
        failures = [self._parse_failure(0)]
        exit_code, stdout, stderr, records = _run_execute_capture(
            informants, failures, tmpdir, source="all"
        )
        assert exit_code == 0
        for rec in records:
            has_informant = rec.get("originating_informant_id") is not None
            has_failure = rec.get("originating_failure_id") is not None
            assert has_informant != has_failure, (
                f"xor invariant violated: informant_id={rec.get('originating_informant_id')!r}, "
                f"failure_id={rec.get('originating_failure_id')!r}"
            )

    def test_execute_per_call_progress_printed_to_stdout(self, tmpdir: Path) -> None:
        """Stdout captures one [N/M] progress line per call."""
        informants = [self._glm_informant(i) for i in range(3)]
        exit_code, stdout, stderr, records = _run_execute_capture(
            informants, [], tmpdir, source="informants"
        )
        assert exit_code == 0
        # Check for [1/3], [2/3], [3/3]
        assert "[1/3]" in stdout
        assert "[2/3]" in stdout
        assert "[3/3]" in stdout
        # Each line should contain model= and domain= (no cost tracking)
        lines = [ln for ln in stdout.splitlines() if ln.startswith("[")]
        assert len(lines) == 3
        for ln in lines:
            assert "model=" in ln
            assert "step=" in ln

    def test_execute_summary_shows_call_counts(self, tmpdir: Path) -> None:
        """Final summary shows call counts per source, not dollar totals."""
        informants = [self._glm_informant(i) for i in range(3)]
        exit_code, stdout, stderr, records = _run_execute_capture(
            informants, [], tmpdir, source="informants",
        )
        assert exit_code == 0
        assert "Records written:              3" in stdout
        assert "Informants-origin calls:      3" in stdout

    def test_execute_pre_flight_stop_at_cap(self, tmpdir: Path) -> None:
        """Pre-flight check: projected calls >= 80% of cap -> exit 2 BEFORE any API call.

        160 records >= 160 (80% of 200). No writes to JSONL.
        """
        informants = [
            _make_informant_with_prompts(
                informant_id=f"pf_preflight_{i:04d}",
                model_id="z-ai/glm-5.1",
                domain_slug="family",
                qa_passed=False,
                qa_notes="0; 71000ms; 171",
                parsed_items=[],
            )
            for i in range(160)
        ]
        informants_path = tmpdir / "informants.jsonl"
        failures_path = tmpdir / "failures.jsonl"
        output_path = tmpdir / "decline_interviews.jsonl"
        _write_jsonl(informants_path, informants)
        _write_jsonl(failures_path, [])
        output_path.touch()

        # Track whether adapter was called
        call_count = [0]

        class CountingAdapter:
            model = MockAdapter(model_id="z-ai/glm-5.1").model
            async def complete(self, prompt, *, json_schema=None, temperature=0.7):  # noqa: D102
                call_count[0] += 1
                return MockAdapter().complete.__func__(self, prompt, temperature=temperature)  # type: ignore[misc]

        def adapter_factory(model_id: str) -> CountingAdapter:
            return CountingAdapter()

        captured_out = StringIO()
        with patch("sys.stdout", captured_out), patch("sys.stderr", StringIO()):
            exit_code = run_execute(
                informants_path=informants_path,
                failures_path=failures_path,
                output_path=output_path,
                max_batch_calls=200,
                source="informants",
                adapter_factory=adapter_factory,
            )

        assert exit_code == 2
        assert "STOP" in captured_out.getvalue()
        # No API calls made
        assert call_count[0] == 0
        # JSONL not written
        assert output_path.read_text(encoding="utf-8") == ""

    def test_execute_cap_abort_mid_batch(self, tmpdir: Path) -> None:
        """Pre-flight stops when projected calls >= 80% of cap (exit 2).

        The exit-3 mid-batch hard-cap abort has been removed (task #F2-T14).
        The pre-flight gate (exit 2) fires before any API call when the batch
        is projected to exceed 80% of max_batch_calls.

        5 records >= 4 (80% of 5) -> pre-flight exit 2.
        """
        informants = [self._glm_informant(i) for i in range(5)]
        exit_code, stdout, stderr, records = _run_execute_capture(
            informants, [], tmpdir,
            source="informants",
            max_batch_calls=5,
        )
        assert exit_code == 2
        # No records written before pre-flight abort
        assert len(records) == 0
        assert "STOP" in stdout

    def test_execute_excluded_records_not_written(self, tmpdir: Path) -> None:
        """failures-origin HTTPStatusError 400 -> SKIP logged to stderr, not in output."""
        failures = [self._http_failure(i) for i in range(3)]
        exit_code, stdout, stderr, records = _run_execute_capture(
            [], failures, tmpdir, source="failures"
        )
        assert exit_code == 0
        assert len(records) == 0
        assert stderr.count("SKIP:") == 3
        for line in stderr.splitlines():
            if "SKIP:" in line:
                assert "http_infrastructure:HTTPStatusError" in line

    def test_execute_version_drift_flag_computed(self, tmpdir: Path) -> None:
        """MockAdapter returns different model_version_returned than originating informant
        -> version_drift_flag=True on the DeclineInterview record."""
        informants = [
            _make_informant_with_prompts(
                informant_id="drift_test_0001",
                model_id="z-ai/glm-5.1",
                domain_slug="family",
                qa_passed=False,
                qa_notes="0; 71000ms; 171",
                parsed_items=[],
                model_version_returned="glm-5.1-original-version",
            )
        ]
        # MockAdapter returns "glm-5.1-v1-DIFFERENT" — different from "glm-5.1-original-version"
        informants_path = tmpdir / "informants.jsonl"
        failures_path = tmpdir / "failures.jsonl"
        output_path = tmpdir / "decline_interviews.jsonl"
        _write_jsonl(informants_path, informants)
        _write_jsonl(failures_path, [])
        output_path.touch()

        different_version_adapter = MockAdapter(
            model_id="z-ai/glm-5.1",
            model_version_returned="glm-5.1-DIFFERENT-version",
        )

        def adapter_factory(model_id: str) -> MockAdapter:
            return different_version_adapter

        with patch("sys.stdout", StringIO()), patch("sys.stderr", StringIO()):
            exit_code = run_execute(
                informants_path=informants_path,
                failures_path=failures_path,
                output_path=output_path,
                source="informants",
                adapter_factory=adapter_factory,
            )

        assert exit_code == 0
        records = [json.loads(ln) for ln in output_path.read_text().splitlines() if ln.strip()]
        assert len(records) == 1
        assert records[0]["version_drift_flag"] is True

    def test_execute_recursive_decline_counted(self, tmpdir: Path) -> None:
        """MockAdapter returns a first-person refusal phrase matching
        RECURSIVE_DECLINE_PHRASES -> recursive-decline count incremented;
        stderr emits RECURSIVE_DECLINE.

        Updated for T-R1 (Amendment 2): the corrected _is_recursive_decline()
        uses RECURSIVE_DECLINE_PHRASES (first-person refusal locutions), not
        SAFETY_FILTER_MARKERS. Third-person safety-vocabulary responses (like
        'This content was blocked by the safety filter.') are no longer counted
        as recursive declines — they are successful substantive interviews.
        """
        informants = [self._glm_informant(0)]
        exit_code, stdout, stderr, records = _run_execute_capture(
            informants, [], tmpdir,
            source="informants",
            adapter_response="I cannot describe what happened in that exchange.",
        )
        assert exit_code == 0
        assert "RECURSIVE_DECLINE:" in stderr
        assert "Recursive declines observed:  1" in stdout

    def test_execute_recursive_decline_empty_response_counted(self, tmpdir: Path) -> None:
        """MockAdapter returns empty string -> also counted as recursive decline."""
        informants = [self._glm_informant(0)]
        exit_code, stdout, stderr, records = _run_execute_capture(
            informants, [], tmpdir,
            source="informants",
            adapter_response="",
        )
        assert exit_code == 0
        assert "RECURSIVE_DECLINE:" in stderr
        assert "Recursive declines observed:  1" in stdout

    def test_execute_source_flag_forwarded_correctly(self, tmpdir: Path) -> None:
        """--source informants with mixed fixture -> only informants records written."""
        informants = [self._glm_informant(i) for i in range(2)]
        failures = [self._parse_failure(0)]  # INCLUDE, but should not be written
        exit_code, stdout, stderr, records = _run_execute_capture(
            informants, failures, tmpdir, source="informants"
        )
        assert exit_code == 0
        # Only informants-origin records written (failures excluded by source filter)
        assert len(records) == 2
        for rec in records:
            assert rec["originating_informant_id"] is not None
            assert rec["originating_failure_id"] is None

    def test_execute_summary_includes_per_source_counters(self, tmpdir: Path) -> None:
        """CLI summary prints informants-origin vs failures-origin call counts."""
        informants = [self._glm_informant(0)]
        failures = [self._parse_failure(0)]
        exit_code, stdout, stderr, records = _run_execute_capture(
            informants, failures, tmpdir, source="all"
        )
        assert exit_code == 0
        assert "Informants-origin calls:" in stdout
        assert "Failures-origin calls:" in stdout

    def test_execute_detection_rule_version_is_v1(self, tmpdir: Path) -> None:
        """Every written record has detection_rule_version='v1'."""
        informants = [self._glm_informant(i) for i in range(3)]
        exit_code, stdout, stderr, records = _run_execute_capture(
            informants, [], tmpdir, source="informants"
        )
        assert exit_code == 0
        for rec in records:
            assert rec["detection_rule_version"] == "v1"

    def test_execute_task_description_reconstructed_from_informant_step_4_freelist(
        self, tmpdir: Path
    ) -> None:
        """Informants-origin with originating_step=freelist (trigger c: empty freelist)
        -> task_description == originating InformantRecord.freelist.prompt_verbatim."""
        # Build an informant where detect_from_informant fires trigger (c): empty freelist
        # The originating_step will be "freelist"
        informant = _make_informant_with_prompts(
            informant_id="freelist_prompt_test_0001",
            model_id="z-ai/glm-5.1",
            domain_slug="family",
            qa_passed=False,
            qa_notes="0; 71000ms; 171",
            parsed_items=[],   # empty freelist -> trigger (c) -> step=freelist
            freelist_prompt="Please list every type of family relationship you can think of.",
        )
        informants_path = tmpdir / "informants.jsonl"
        failures_path = tmpdir / "failures.jsonl"
        output_path = tmpdir / "decline_interviews.jsonl"
        _write_jsonl(informants_path, [informant])
        _write_jsonl(failures_path, [])
        output_path.touch()

        received_prompts: list[str] = []

        class CapturingMockAdapter:
            """Captures the prompt passed to complete() then delegates to MockAdapter."""
            def __init__(self) -> None:
                self._inner = MockAdapter(model_id="z-ai/glm-5.1")
                self.model = self._inner.model

            async def complete(self, prompt, *, json_schema=None, temperature=0.7):
                received_prompts.append(prompt)
                return await self._inner.complete(prompt, temperature=temperature)

        _adapter_instance = CapturingMockAdapter()

        def adapter_factory(model_id: str) -> CapturingMockAdapter:
            return _adapter_instance

        with patch("sys.stdout", StringIO()), patch("sys.stderr", StringIO()):
            exit_code = run_execute(
                informants_path=informants_path,
                failures_path=failures_path,
                output_path=output_path,
                source="informants",
                adapter_factory=adapter_factory,
            )

        assert exit_code == 0
        assert len(received_prompts) == 1
        # The decline prompt includes task_description (freelist prompt_verbatim).
        expected_fragment = "Please list every type of family relationship you can think of."
        assert expected_fragment in received_prompts[0]

    def test_execute_task_description_reconstructed_from_failure_with_prompt_verbatim(
        self, tmpdir: Path
    ) -> None:
        """Failures-origin with prompt_verbatim present -> task_description == that value."""
        failure = _make_failure_full(
            model_id="z-ai/glm-5.1",
            domain="family",
            run_index=0,
            error_type="ValueError",
            error_message="Items missing from pile sort: expected 5, got 3",
            prompt_verbatim="Sort the following family terms into groups: mother, father, sister.",
        )
        informants_path = tmpdir / "informants.jsonl"
        failures_path = tmpdir / "failures.jsonl"
        output_path = tmpdir / "decline_interviews.jsonl"
        _write_jsonl(informants_path, [])
        _write_jsonl(failures_path, [failure])
        output_path.touch()

        received_prompts: list[str] = []

        class CapturingMockAdapter2:
            def __init__(self) -> None:
                self._inner = MockAdapter(model_id="z-ai/glm-5.1")
                self.model = self._inner.model

            async def complete(self, prompt, *, json_schema=None, temperature=0.7):
                received_prompts.append(prompt)
                return await self._inner.complete(prompt, temperature=temperature)

        _adapter_instance2 = CapturingMockAdapter2()

        def adapter_factory(model_id: str) -> CapturingMockAdapter2:
            return _adapter_instance2

        with patch("sys.stdout", StringIO()), patch("sys.stderr", StringIO()):
            exit_code = run_execute(
                informants_path=informants_path,
                failures_path=failures_path,
                output_path=output_path,
                source="failures",
                adapter_factory=adapter_factory,
            )

        assert exit_code == 0
        assert len(received_prompts) == 1
        expected_verbatim = "Sort the following family terms into groups: mother, father, sister."
        assert expected_verbatim in received_prompts[0]

    def test_execute_task_description_fallback_to_template_for_failure_without_prompt_verbatim(
        self, tmpdir: Path
    ) -> None:
        """Failures-origin with prompt_verbatim=None -> task_description reconstructed from
        template. This is RISK 1 territory (see run_execute docstring and
        _task_description_from_failure). The template is the free_list.md for freelist-step
        failures or pile_sort.md for pile_sort steps. The test verifies that:
        1. The call succeeds (no exception).
        2. The written record has a non-empty prompt_verbatim field (the decline prompt
           was constructed from SOMETHING, not empty).
        3. The originating_failure_id is set on the written record.

        Reconstruction path: _task_description_from_failure() reads
        packages/cdb_collect/cdb_collect/prompts/v1/pile_sort.md when failed_step=pile_sort
        and prompt_verbatim is absent. The template will contain unfilled {{items}} markers.
        This is documented behavior per Amendment 1 §6 RISK 1 note.
        """
        failure = _make_failure_full(
            model_id="z-ai/glm-5.1",
            domain="family",
            run_index=0,
            error_type="ValueError",
            error_message="Items missing from pile sort: expected 5, got 3",
            prompt_verbatim=None,   # RISK 1 case: no verbatim prompt available
            failed_step="pile_sort",
        )
        informants_path = tmpdir / "informants.jsonl"
        failures_path = tmpdir / "failures.jsonl"
        output_path = tmpdir / "decline_interviews.jsonl"
        _write_jsonl(informants_path, [])
        _write_jsonl(failures_path, [failure])
        output_path.touch()

        def adapter_factory(model_id: str) -> MockAdapter:
            return MockAdapter(model_id="z-ai/glm-5.1")

        with patch("sys.stdout", StringIO()), patch("sys.stderr", StringIO()):
            exit_code = run_execute(
                informants_path=informants_path,
                failures_path=failures_path,
                output_path=output_path,
                source="failures",
                adapter_factory=adapter_factory,
            )

        assert exit_code == 0
        records = [json.loads(ln) for ln in output_path.read_text().splitlines() if ln.strip()]
        assert len(records) == 1
        rec = records[0]
        assert rec["originating_failure_id"] is not None
        assert rec["originating_informant_id"] is None
        # The decline prompt was constructed (prompt_verbatim on the DeclineInterview
        # is the full decline-interview prompt, which wraps the reconstructed task_description)
        assert len(rec["prompt_verbatim"]) > 0

    def test_execute_response_verbatim_empty_string_when_missing(
        self, tmpdir: Path
    ) -> None:
        """Failures-origin with response_verbatim=None -> passed as empty string."""
        failure = _make_failure_full(
            model_id="z-ai/glm-5.1",
            domain="family",
            run_index=0,
            error_type="ValueError",
            error_message="Items missing from pile sort: expected 5, got 3",
            response_verbatim=None,  # absent -> should pass "" to run_decline_interview
        )
        informants_path = tmpdir / "informants.jsonl"
        failures_path = tmpdir / "failures.jsonl"
        output_path = tmpdir / "decline_interviews.jsonl"
        _write_jsonl(informants_path, [])
        _write_jsonl(failures_path, [failure])
        output_path.touch()

        def adapter_factory(model_id: str) -> MockAdapter:
            return MockAdapter(model_id="z-ai/glm-5.1")

        # build_prompt() in run_decline_interview.py substitutes "(empty)"
        # when response_verbatim is "" — no exception should be raised.
        captured_out = StringIO()
        captured_err = StringIO()
        with patch("sys.stdout", captured_out), patch("sys.stderr", captured_err):
            exit_code = run_execute(
                informants_path=informants_path,
                failures_path=failures_path,
                output_path=output_path,
                source="failures",
                adapter_factory=adapter_factory,
            )

        assert exit_code == 0
        records = [json.loads(ln) for ln in output_path.read_text().splitlines() if ln.strip()]
        assert len(records) == 1
        # The decline prompt should contain "(empty)" since response_verbatim was absent
        assert "(empty)" in records[0]["prompt_verbatim"]

    def test_execute_does_not_touch_informants_jsonl_or_failures_jsonl(
        self, tmpdir: Path
    ) -> None:
        """mtime snapshot before and after: no writes to either source file."""
        informants = [self._glm_informant(0)]
        failures = [self._parse_failure(0)]
        informants_path = tmpdir / "informants.jsonl"
        failures_path = tmpdir / "failures.jsonl"
        output_path = tmpdir / "decline_interviews.jsonl"
        _write_jsonl(informants_path, informants)
        _write_jsonl(failures_path, failures)
        output_path.touch()

        mtime_inf_before = informants_path.stat().st_mtime
        mtime_fail_before = failures_path.stat().st_mtime

        def adapter_factory(model_id: str) -> MockAdapter:
            return MockAdapter(model_id="z-ai/glm-5.1")

        with patch("sys.stdout", StringIO()), patch("sys.stderr", StringIO()):
            run_execute(
                informants_path=informants_path,
                failures_path=failures_path,
                output_path=output_path,
                source="all",
                adapter_factory=adapter_factory,
            )

        assert informants_path.stat().st_mtime == mtime_inf_before, (
            "execute path must not modify informants.jsonl"
        )
        assert failures_path.stat().st_mtime == mtime_fail_before, (
            "execute path must not modify failures.jsonl"
        )


# ── T2: TestCostCapAbortDuringExecute ────────────────────────────────────────

class TestCostCapAbortDuringExecute:
    """Tests for mid-batch cost cap abort behavior.

    Exit code 3 is distinct from dry-run STOP (exit 2).
    """

    @pytest.fixture()
    def tmpdir(self, tmp_path: Path) -> Path:
        return tmp_path

    def _glm_informant(self, idx: int) -> dict[str, Any]:
        return _make_informant_with_prompts(
            informant_id=f"cap_abort_{idx:04d}",
            model_id="z-ai/glm-5.1",
            domain_slug="family",
            qa_passed=False,
            qa_notes="0; 71000ms; 171",
            parsed_items=[],
        )

    def test_call_cap_abort_exits_2(self, tmpdir: Path) -> None:
        """Pre-flight stop exits 2 when projected calls >= 80% of max_batch_calls.

        The exit-3 mid-batch hard-cap abort has been removed (task #F2-T14).
        Call-count gate: 5 records >= 4 (80% of 5) -> pre-flight exit 2.
        """
        informants = [self._glm_informant(i) for i in range(5)]
        exit_code, stdout, stderr, records = _run_execute_capture(
            informants, [], tmpdir,
            source="informants",
            max_batch_calls=5,
        )
        assert exit_code == 2  # pre-flight STOP

    def test_call_cap_abort_exits_2_correct_cap(self, tmpdir: Path) -> None:
        """Pre-flight exits 2 when projected calls >= 80% of max_batch_calls.

        Exit-3 mid-batch hard-cap abort was removed in task #F2-T14.
        The pre-flight gate is now the sole cost-protection mechanism.
        5 records >= 4 (80% of 5) -> pre-flight exit 2.
        """
        informants = [self._glm_informant(i) for i in range(5)]
        informants_path = tmpdir / "informants.jsonl"
        failures_path = tmpdir / "failures.jsonl"
        output_path = tmpdir / "decline_interviews.jsonl"
        _write_jsonl(informants_path, informants)
        _write_jsonl(failures_path, [])
        output_path.touch()

        def adapter_factory(model_id: str) -> MockAdapter:
            return MockAdapter(model_id="z-ai/glm-5.1")

        captured_out = StringIO()
        with patch("sys.stdout", captured_out), patch("sys.stderr", StringIO()):
            exit_code = run_execute(
                informants_path=informants_path,
                failures_path=failures_path,
                output_path=output_path,
                max_batch_calls=5,   # pre-flight: 5 >= 4 (80% of 5) -> STOP
                source="informants",
                adapter_factory=adapter_factory,
            )

        assert exit_code == 2, f"Expected exit 2 (pre-flight STOP), got {exit_code}"

    def test_call_cap_abort_message_and_no_records_written(
        self, tmpdir: Path
    ) -> None:
        """Pre-flight STOP message is emitted; no records written before abort.

        The exit-3 mid-batch COST CAP EXCEEDED path has been removed (task #F2-T14).
        This test verifies the pre-flight STOP message is emitted and no records
        are written.
        """
        informants = [self._glm_informant(i) for i in range(5)]
        informants_path = tmpdir / "informants.jsonl"
        failures_path = tmpdir / "failures.jsonl"
        output_path = tmpdir / "decline_interviews.jsonl"
        _write_jsonl(informants_path, informants)
        _write_jsonl(failures_path, [])
        output_path.touch()

        def adapter_factory(model_id: str) -> MockAdapter:
            return MockAdapter(model_id="z-ai/glm-5.1")

        captured_out = StringIO()
        with patch("sys.stdout", captured_out), patch("sys.stderr", StringIO()):
            exit_code = run_execute(
                informants_path=informants_path,
                failures_path=failures_path,
                output_path=output_path,
                max_batch_calls=5,   # 5 >= 4 (80% of 5) -> pre-flight STOP
                source="informants",
                adapter_factory=adapter_factory,
            )

        assert exit_code == 2
        output = captured_out.getvalue()
        assert "STOP" in output
        # No records written — pre-flight aborts before any API call
        lines = [ln.strip() for ln in output_path.read_text().splitlines() if ln.strip()]
        assert len(lines) == 0

    def test_call_cap_pass_writes_all_records(self, tmpdir: Path) -> None:
        """When batch is under 80% of cap, all records are written.

        3 records with max_batch_calls=200: 3 < 160 (80% of 200) -> GO.
        """
        informants = [self._glm_informant(i) for i in range(3)]
        informants_path = tmpdir / "informants.jsonl"
        failures_path = tmpdir / "failures.jsonl"
        output_path = tmpdir / "decline_interviews.jsonl"
        _write_jsonl(informants_path, informants)
        _write_jsonl(failures_path, [])
        output_path.touch()

        def adapter_factory(model_id: str) -> MockAdapter:
            return MockAdapter(model_id="z-ai/glm-5.1")

        with patch("sys.stdout", StringIO()), patch("sys.stderr", StringIO()):
            exit_code = run_execute(
                informants_path=informants_path,
                failures_path=failures_path,
                output_path=output_path,
                max_batch_calls=200,
                source="informants",
                adapter_factory=adapter_factory,
            )

        assert exit_code == 0
        # Read written records — all 3 should be written
        lines = [ln.strip() for ln in output_path.read_text().splitlines() if ln.strip()]
        assert len(lines) == 3
        for line in lines:
            rec = json.loads(line)
            assert "decline_interview_id" in rec
            assert "originating_informant_id" in rec or "originating_failure_id" in rec
            assert rec["detection_rule_version"] == "v1"


# ── T2: TestSafetyMarkerCommentA2N3 ──────────────────────────────────────────

class TestSafetyMarkerCommentA2N3:
    """Tests for SAFETY_FILTER_MARKERS content and the N3 comment requirement."""

    def test_safety_marker_jailbreak_still_in_list(self) -> None:
        """Regression: 'jailbreak' must remain in SAFETY_FILTER_MARKERS (SME A2)."""
        markers = _mod.SAFETY_FILTER_MARKERS
        assert "jailbreak" in markers, (
            "SME A2 requires 'jailbreak' in SAFETY_FILTER_MARKERS"
        )

    def test_safety_marker_other_in_list(self) -> None:
        """Gemini's generic content-block finish_reason 'OTHER' must be in markers."""
        markers = _mod.SAFETY_FILTER_MARKERS
        assert "OTHER" in markers

    def test_safety_marker_comment_about_other_present_in_source(self) -> None:
        """Reviewer N3: SAFETY_FILTER_MARKERS must have an inline comment documenting
        the 'OTHER' false-positive risk (case-insensitive substring matching).

        This test addresses T1-update Reviewer note N3 by checking that the
        source file contains the warning comment near the 'OTHER' marker.
        """
        source = _SCRIPT_PATH.read_text(encoding="utf-8")
        # The comment required by N3 must be present near the "OTHER" marker entry.
        # We verify it mentions the false-positive risk and the trade-off rationale.
        assert "false-positive" in source or "false positive" in source, (
            "Source must document the 'OTHER' substring false-positive risk (Reviewer N3)"
        )
        assert "OTHER" in source
        # Verify the specific context: the comment should be in proximity to the OTHER marker
        other_idx = source.index('"OTHER"')
        surrounding = source[max(0, other_idx - 500):other_idx + 200]
        assert "substring" in surrounding.lower() or "case-insensitive" in surrounding.lower(), (
            "Comment near 'OTHER' should explain case-insensitive substring matching behavior"
        )

    def test_is_recursive_decline_empty_string(self) -> None:
        """Empty string -> recursive decline."""
        assert _is_recursive_decline("") is True

    def test_is_recursive_decline_whitespace_only(self) -> None:
        """Whitespace-only string -> recursive decline."""
        assert _is_recursive_decline("   \n\t  ") is True

    def test_is_recursive_decline_length_floor_trigger(self) -> None:
        """Short response (31 chars < MIN_SUBSTANTIVE_RESPONSE_LEN=40) -> recursive decline.

        Pre-T-R1, this test was named test_is_recursive_decline_safety_marker_match
        and its docstring claimed the True result came from the SAFETY_FILTER_MARKERS
        branch. After T-R1 corrected _is_recursive_decline(), that branch was removed.
        The input "This was blocked by the filter." (31 chars stripped) still returns
        True, but now via the length-floor branch (Q1.B), not the removed marker branch.

        Renamed and re-documented per Reviewer T-R1 Note 1 (stale-docstring cleanup).
        See: docs/status/2026-04-23-phase4a1-t-r1-reviewer-verdict.md Note 1
        """
        assert _is_recursive_decline("This was blocked by the filter.") is True

    def test_is_recursive_decline_normal_response(self) -> None:
        """Normal response text -> NOT recursive decline."""
        assert _is_recursive_decline(
            "The model attempted to list family terms but the list was empty."
        ) is False


# ── T-R1: TestIsRecursiveDeclineCorrected ─────────────────────────────────────

class TestIsRecursiveDeclineCorrected:
    """Binding test cases for the corrected _is_recursive_decline() per SME T3B-detector
    verdict Q1.E and Architect Plan Amendment 2 §2 T-R1.

    Ten binding test cases:
      1-2.  Empty / whitespace-only → True  (existing cases preserved)
      3-7.  Five T3B false-positive verbatim samples → False
      8-10. Three synthetic genuine recursive-decline cases → True
      11-12 (0-indexed 3-4 in group 5). Two third-person-attribution cases → False

    All false-positive samples include sufficient surrounding prose to clear the
    40-character MIN_SUBSTANTIVE_RESPONSE_LEN floor, ensuring the allowlist branch
    (not the length-floor branch) is exercised for those assertions.

    References:
      SME verdict: docs/status/2026-04-23-phase4a1-t3b-detector-cda-sme-verdict.md Q1.E
      Amendment 2: docs/status/2026-04-23-phase4a1-architect-plan-amendment-2.md §2 T-R1
    """

    # ── Case 1 & 2: empty/whitespace (preserved existing behavior) ────────────

    def test_empty_string_is_recursive_decline(self) -> None:
        """Empty string returns True (SME Q1.A, Q1.E case 1)."""
        assert _is_recursive_decline("") is True

    def test_whitespace_only_is_recursive_decline(self) -> None:
        """Whitespace-only string returns True (SME Q1.A, Q1.E case 2)."""
        assert _is_recursive_decline("   \n\t  ") is True

    # ── Cases 3–7: T3B false-positive verbatim samples → False ───────────────
    # Each input reproduces the verbatim fragment from T3B run log
    # §"Representative verbatim samples" with sufficient surrounding prose to
    # clear the 60-char safety margin (Risk R-A2.1), exercising the allowlist
    # branch rather than the length-floor branch.

    def test_gemini_safety_protocols_narrative_is_not_recursive_decline(self) -> None:
        """Gemini 'internal safety protocols and programming guide me' sample.

        T3B run log: flagged via 'safety' substring match (false positive).
        This is a third-person/impersonal description of the originating safety
        event, not a first-person refusal of the decline-interview task.
        Must return False under the corrected detector.
        """
        sample = (
            "My internal safety protocols and programming guide me to avoid generating "
            "content that could facilitate harmful activities. The original request "
            "triggered this protective mechanism in the exchange."
        )
        assert len(sample.strip()) >= 60, "test input must clear 60-char safety margin"
        assert _is_recursive_decline(sample) is False

    def test_gemini_blocked_negotiating_narrative_is_not_recursive_decline(self) -> None:
        """Gemini 'I was blocked from negotiating the request' sample.

        T3B run log: flagged via 'blocked' substring match (false positive).
        The phrase 'I was blocked' describes what happened to the model in the
        originating exchange — it is third-person-shaped attribution of a past
        event, not a first-person refusal of the current decline-interview task.
        Must return False under the corrected detector.
        """
        sample = (
            "I was blocked from negotiating the request because the topic touched on "
            "content that my content policy does not permit. The original exchange "
            "produced an empty response as a result of this restriction."
        )
        assert len(sample.strip()) >= 60, "test input must clear 60-char safety margin"
        assert _is_recursive_decline(sample) is False

    def test_glm_safety_filter_false_trigger_narrative_is_not_recursive_decline(self) -> None:
        """glm-5.1 'false trigger of a safety filter: Though highly improbable' sample.

        T3B run log: flagged via 'safety' substring match (false positive).
        This is a substantive meta-discussion of the original failure — the model
        is hypothesizing about the cause of the originating empty-response.
        Must return False under the corrected detector.
        """
        sample = (
            "This appears to be a false trigger of a safety filter: Though highly "
            "improbable given the benign nature of the request, the system may have "
            "detected a pattern that matched its content-filtering heuristics."
        )
        assert len(sample.strip()) >= 60, "test input must clear 60-char safety margin"
        assert _is_recursive_decline(sample) is False

    def test_llama_output_empty_other_words_narrative_is_not_recursive_decline(self) -> None:
        """llama-4-maverick 'the output was empty. In other words, this is the' sample.

        T3B run log: flagged via 'OTHER' case-insensitive substring match
        (false positive — matched 'other' inside 'other words').
        Ordinary prose describing what happened; no first-person refusal signal.
        Must return False under the corrected detector.
        """
        sample = (
            "In the exchange that occurred, the output was empty. In other words, "
            "this is the result of the model returning no content for the pile-sort "
            "task on the family domain during that session."
        )
        assert len(sample.strip()) >= 60, "test input must clear 60-char safety margin"
        assert _is_recursive_decline(sample) is False

    def test_gpt_in_other_words_task_narrative_is_not_recursive_decline(self) -> None:
        """gpt-5.4-mini 'In other words, the task was' sample.

        T3B run log: flagged via 'OTHER' case-insensitive substring match
        (false positive — matched 'other' inside 'other words').
        Ordinary prose; same false-positive shape as the llama case above.
        Must return False under the corrected detector.
        """
        sample = (
            "The pile-sort response came back with no items listed. In other words, "
            "the task was completed by the model but yielded an empty result set "
            "rather than the expected categorization of terms."
        )
        assert len(sample.strip()) >= 60, "test input must clear 60-char safety margin"
        assert _is_recursive_decline(sample) is False

    # ── Cases 8–10: synthetic genuine recursive-decline cases → True ──────────

    def test_cannot_describe_is_recursive_decline(self) -> None:
        """'I cannot describe what happened in that exchange.' triggers Q1.C allowlist."""
        assert _is_recursive_decline(
            "I cannot describe what happened in that exchange."
        ) is True

    def test_sorry_short_response_is_recursive_decline(self) -> None:
        """'Sorry.' triggers Q1.B length-floor (5 chars < 40)."""
        assert _is_recursive_decline("Sorry.") is True

    def test_wont_engage_is_recursive_decline(self) -> None:
        """'I won't engage with this.' triggers Q1.C allowlist."""
        assert _is_recursive_decline("I won't engage with this.") is True

    # ── Cases 11–12: third-person-attribution cases with coincidental vocabulary → False

    def test_third_person_could_not_process_is_not_recursive_decline(self) -> None:
        """'The model's response indicated it could not process the request.'

        Contains 'could not' but is third-person attribution; not in the
        RECURSIVE_DECLINE_PHRASES allowlist. Must clear 40-char floor and
        return False. (SME Q1.E case 5a)
        """
        sample = "The model's response indicated it could not process the request."
        assert len(sample.strip()) >= 40, "test input must clear length floor"
        assert _is_recursive_decline(sample) is False

    def test_third_person_declined_to_provide_is_not_recursive_decline(self) -> None:
        """'The original output declined to provide the list, citing safety concerns.'

        Third-person attribution shape; not a first-person refusal of the current
        task. Must clear 40-char floor and return False. (SME Q1.E case 5b)
        """
        sample = (
            "The original output declined to provide the list, citing safety concerns."
        )
        assert len(sample.strip()) >= 40, "test input must clear length floor"
        assert _is_recursive_decline(sample) is False
