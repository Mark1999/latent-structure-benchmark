"""Unit tests for qa/divergence.py (T7).

No real subprocess. run_checks_fn is injectable. tmp_path only.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from cdb_social.admin_console.qa.divergence import DivergenceRow, compute_divergence

FIXTURES = Path(__file__).parent.parent.parent / "fixtures" / "ops_console"


# ---------------------------------------------------------------------------
# Fake check functions
# ---------------------------------------------------------------------------


class _FakeFailure:
    def __init__(self, check_num: int) -> None:
        self.check_num = check_num


def _always_pass(record: Any, all_records: Any = None) -> list[Any]:
    return []


def _always_fail(record: Any, all_records: Any = None) -> list[_FakeFailure]:
    return [_FakeFailure(1)]


def _check_fn_for_informant_id(iid: str, check_nums: list[int]):
    """Fail only for a specific informant_id; pass for all others."""

    def fn(record: Any, all_records: Any = None) -> list[_FakeFailure]:
        if getattr(record, "informant_id", "") == iid:
            return [_FakeFailure(n) for n in check_nums]
        return []

    return fn


# ---------------------------------------------------------------------------
# Empty / missing informants.jsonl
# ---------------------------------------------------------------------------


class TestEmptyInput:
    def test_returns_empty_for_absent_file(self, tmp_path: Path) -> None:
        result = compute_divergence(
            tmp_path / "missing.jsonl", run_checks_fn=_always_pass
        )
        assert result == []

    def test_returns_empty_for_empty_file(self, tmp_path: Path) -> None:
        empty = tmp_path / "informants.jsonl"
        empty.write_text("", encoding="utf-8")
        result = compute_divergence(empty, run_checks_fn=_always_pass)
        assert result == []

    def test_returns_empty_when_all_invalid_json(self, tmp_path: Path) -> None:
        bad = tmp_path / "informants.jsonl"
        bad.write_text("not json\n", encoding="utf-8")
        result = compute_divergence(bad, run_checks_fn=_always_pass)
        assert result == []


# ---------------------------------------------------------------------------
# Divergence detection with the qa fixture
# ---------------------------------------------------------------------------


class TestDivergenceDetection:
    """Uses informants_qa.jsonl:
    - qa-001: qa_passed=True, recomputed=PASS -> no divergence
    - qa-002: qa_passed=True, recomputed=PASS -> no divergence
    - qa-003: qa_passed=False, recomputed=PASS -> DIVERGENCE
    - qa-004: qa_passed=True, recomputed=FAIL(check 1) -> DIVERGENCE
    """

    def test_no_divergence_when_checks_match(self) -> None:
        # All records have qa_passed=True; if checks all pass, no divergence.
        # But qa-003 is qa_passed=False, so it would diverge with _always_pass.
        result = compute_divergence(
            FIXTURES / "informants_qa.jsonl",
            run_checks_fn=_always_fail,
        )
        # With _always_fail: check returns [failure] for all records.
        # recomputed_passed = False for all records.
        # qa-001, qa-002, qa-004: persisted=True, recomputed=False -> diverge
        # qa-003: persisted=False, recomputed=False -> no diverge
        informant_ids = {r.informant_id for r in result}
        assert "qa-001" in informant_ids
        assert "qa-002" in informant_ids
        assert "qa-004" in informant_ids
        assert "qa-003" not in informant_ids

    def test_persisted_false_but_recomputed_pass_is_divergence(self) -> None:
        # qa-003 has qa_passed=False but _always_pass returns no failures.
        result = compute_divergence(
            FIXTURES / "informants_qa.jsonl",
            run_checks_fn=_always_pass,
        )
        ids = {r.informant_id for r in result}
        assert "qa-003" in ids

    def test_persisted_true_but_recomputed_fail_is_divergence(self) -> None:
        # Fail only for qa-004 (qa_passed=True).
        check_fn = _check_fn_for_informant_id("qa-004", [1])
        result = compute_divergence(
            FIXTURES / "informants_qa.jsonl",
            run_checks_fn=check_fn,
        )
        ids = {r.informant_id for r in result}
        assert "qa-004" in ids

    def test_divergence_row_fields_are_correct(self) -> None:
        check_fn = _check_fn_for_informant_id("qa-004", [1])
        result = compute_divergence(
            FIXTURES / "informants_qa.jsonl",
            run_checks_fn=check_fn,
        )
        row = next(r for r in result if r.informant_id == "qa-004")
        assert isinstance(row, DivergenceRow)
        assert row.model_id == "test-model-a"
        assert row.domain_slug == "holidays"
        assert row.persisted_passed is True
        assert 1 in row.recomputed_check_nums
        assert row.error is None

    def test_no_divergence_for_matching_qa_passed(self) -> None:
        # qa-001 and qa-002 have qa_passed=True; _always_pass -> no divergence.
        result = compute_divergence(
            FIXTURES / "informants_qa.jsonl",
            run_checks_fn=_always_pass,
        )
        ids = {r.informant_id for r in result}
        assert "qa-001" not in ids
        assert "qa-002" not in ids

    def test_recomputed_check_nums_populated(self) -> None:
        check_fn = _check_fn_for_informant_id("qa-001", [2, 5])
        result = compute_divergence(
            FIXTURES / "informants_qa.jsonl",
            run_checks_fn=check_fn,
        )
        row = next(r for r in result if r.informant_id == "qa-001")
        assert sorted(row.recomputed_check_nums) == [2, 5]

    def test_exception_in_check_fn_produces_error_row(self) -> None:
        call_count = [0]

        def exploding_fn(record: Any, all_records: Any = None) -> list[Any]:
            call_count[0] += 1
            if call_count[0] == 1:
                raise RuntimeError("injected error")
            return []

        result = compute_divergence(
            FIXTURES / "informants_qa.jsonl",
            run_checks_fn=exploding_fn,
        )
        error_rows = [r for r in result if r.error is not None]
        assert len(error_rows) >= 1
        assert "injected error" in error_rows[0].error  # type: ignore[operator]

    def test_result_contains_divergence_row_instances(self) -> None:
        result = compute_divergence(
            FIXTURES / "informants_qa.jsonl",
            run_checks_fn=_always_pass,
        )
        for row in result:
            assert isinstance(row, DivergenceRow)
            assert isinstance(row.informant_id, str)
            assert isinstance(row.model_id, str)
            assert isinstance(row.domain_slug, str)
            assert isinstance(row.persisted_passed, bool)
            assert isinstance(row.recomputed_check_nums, list)


# ---------------------------------------------------------------------------
# Real run_record_checks via importlib (integration path)
# ---------------------------------------------------------------------------


class TestRealRunRecordChecks:
    def test_divergence_with_real_checks(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        qa_path = repo_root / "scripts" / "qa_check.py"
        if not qa_path.exists():
            pytest.skip("scripts/qa_check.py not found")

        result = compute_divergence(
            FIXTURES / "informants_qa.jsonl",
            repo_root=repo_root,
        )
        # qa-003: qa_passed=False but recomputed PASS -> divergence
        # qa-004: qa_passed=True but check_1 FAIL -> divergence
        ids = {r.informant_id for r in result}
        assert "qa-003" in ids, "qa-003 (persisted=False, recomputed=PASS) should diverge"
        assert "qa-004" in ids, "qa-004 (persisted=True, check_1=FAIL) should diverge"

    def test_no_divergence_for_consistent_records(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        qa_path = repo_root / "scripts" / "qa_check.py"
        if not qa_path.exists():
            pytest.skip("scripts/qa_check.py not found")

        result = compute_divergence(
            FIXTURES / "informants_qa.jsonl",
            repo_root=repo_root,
        )
        ids = {r.informant_id for r in result}
        # qa-001 and qa-002: persisted=True, recomputed=PASS -> consistent
        assert "qa-001" not in ids
        assert "qa-002" not in ids
