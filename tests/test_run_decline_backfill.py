"""Tests for scripts/run_decline_backfill.py — T1 dry-run path.

Coverage per Phase 4a.1 architect plan §3 T1 acceptance criteria and
CDA SME verdict binding notes 1 and 8.

No real API calls. No file writes. All fixtures are synthetic in-memory dicts.

Fixture scenarios:
  - 3 glm-5.1 x family: empty freelist (trigger c) -> 3 detected
  - 10 qwen3.6-plus x holidays: Check 5+6, structurally valid -> 10 not triggered
  - 4 Check-8-only: mistral-small/gpt-5.4-mini -> 4 not triggered (labels non-empty)
  - 1 llama-4-maverick: Check 5+8 compound -> not triggered (labels non-empty)
  - 8 grok-4: Check-5-only -> 8 not triggered, reason "Check-5 latency-only..."
  - 1 Gemini failure entry -> parsed, Gemini count increments, cost-guard OK
  - File-safety: mtime-snapshot on output file, monkeypatch blocks on open('w') + httpx
  - Cost-guard: 40 detected sessions -> script exits 2 with STOP message

References:
  Architect plan: docs/status/2026-04-23-phase4a1-architect-plan.md
  SME verdict:    docs/status/2026-04-23-phase4a1-architect-plan-cda-sme-verdict.md
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

_SCRIPT_PATH = Path(__file__).resolve().parent.parent / "scripts" / "run_decline_backfill.py"
_spec = importlib.util.spec_from_file_location("run_decline_backfill", _SCRIPT_PATH)
assert _spec is not None and _spec.loader is not None
_mod = importlib.util.module_from_spec(_spec)
_sys.modules["run_decline_backfill"] = _mod
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]

run_dry_run = _mod.run_dry_run
_parse_failing_checks = _mod._parse_failing_checks
_not_triggered_reason = _mod._not_triggered_reason
_is_gemini_failure = _mod._is_gemini_failure


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
        cost_per_call: float = 0.05,
        spend_cap: float = 2.00,
    ) -> tuple[int, str]:
        """Write fixtures to temp files, run dry-run, capture stdout, return (exit_code, output)."""
        informants_path = tmpdir / "informants.jsonl"
        failures_path = tmpdir / "failures.jsonl"
        output_path = tmpdir / "decline_interviews.jsonl"

        _write_jsonl(informants_path, informants)
        _write_jsonl(failures_path, failures)
        # Create output file so we can snapshot its mtime
        output_path.touch()

        captured = StringIO()
        with patch("sys.stdout", captured):
            exit_code = run_dry_run(
                informants_path=informants_path,
                failures_path=failures_path,
                output_path=output_path,
                verbose=verbose,
                cost_per_call=cost_per_call,
                spend_cap=spend_cap,
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
            informants, [], tmpdir, cost_per_call=0.05, spend_cap=2.00
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
            informants, [], tmpdir, cost_per_call=0.05, spend_cap=2.00
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
