"""Unit tests for qa/histogram.py (T7).

No real subprocess. run_checks_fn is injectable. tmp_path only.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from cdb_social.admin_console.qa.histogram import HistogramRow, bucket_failures

FIXTURES = Path(__file__).parent.parent.parent / "fixtures" / "ops_console"


# ---------------------------------------------------------------------------
# Fake QAFailure-like objects
# ---------------------------------------------------------------------------


class _FakeFailure:
    def __init__(self, check_num: int) -> None:
        self.check_num = check_num


def _make_check_fn(*check_nums: int):
    """Return a run_checks_fn that always returns failures for given check numbers."""

    def check_fn(record: Any, all_records: Any = None) -> list[_FakeFailure]:
        return [_FakeFailure(n) for n in check_nums]

    return check_fn


def _no_failures_fn(record: Any, all_records: Any = None) -> list[Any]:
    return []


# ---------------------------------------------------------------------------
# Empty / missing informants.jsonl
# ---------------------------------------------------------------------------


class TestEmptyInput:
    def test_returns_empty_for_absent_file(self, tmp_path: Path) -> None:
        missing = tmp_path / "missing.jsonl"
        result = bucket_failures(missing, run_checks_fn=_no_failures_fn)
        assert result == []

    def test_returns_empty_for_empty_file(self, tmp_path: Path) -> None:
        empty = tmp_path / "informants.jsonl"
        empty.write_text("", encoding="utf-8")
        result = bucket_failures(empty, run_checks_fn=_no_failures_fn)
        assert result == []

    def test_returns_empty_when_all_lines_are_invalid_json(
        self, tmp_path: Path
    ) -> None:
        bad = tmp_path / "informants.jsonl"
        bad.write_text("not json\nalso bad\n", encoding="utf-8")
        result = bucket_failures(bad, run_checks_fn=_no_failures_fn)
        assert result == []


# ---------------------------------------------------------------------------
# Parsing and bucketing with the qa fixture
# ---------------------------------------------------------------------------


class TestBucketFailures:
    """Tests that use the informants_qa.jsonl fixture."""

    def test_no_failures_returns_empty(self) -> None:
        result = bucket_failures(
            FIXTURES / "informants_qa.jsonl",
            run_checks_fn=_no_failures_fn,
        )
        assert result == []

    def test_single_failure_produces_one_row(self) -> None:
        result = bucket_failures(
            FIXTURES / "informants_qa.jsonl",
            run_checks_fn=_make_check_fn(1),
        )
        # 4 records -> 4 failures for check_num=1, but bucketed by model_id.
        # model test-model-a has 3 records, test-model-b has 1.
        assert isinstance(result, list)
        assert len(result) > 0
        for row in result:
            assert isinstance(row, HistogramRow)
            assert row.check_num == 1
            assert row.count > 0

    def test_counts_per_model(self) -> None:
        result = bucket_failures(
            FIXTURES / "informants_qa.jsonl",
            run_checks_fn=_make_check_fn(3),
        )
        counts_by_model = {r.model_id: r.count for r in result}
        # test-model-a has records qa-001, qa-002, qa-004 (3 records)
        assert counts_by_model.get("test-model-a", 0) == 3
        # test-model-b has record qa-003 (1 record)
        assert counts_by_model.get("test-model-b", 0) == 1

    def test_multiple_check_nums_bucketed_separately(self) -> None:
        result = bucket_failures(
            FIXTURES / "informants_qa.jsonl",
            run_checks_fn=_make_check_fn(1, 5),
        )
        check_nums = {r.check_num for r in result}
        assert 1 in check_nums
        assert 5 in check_nums

    def test_result_sorted_by_model_then_check(self) -> None:
        result = bucket_failures(
            FIXTURES / "informants_qa.jsonl",
            run_checks_fn=_make_check_fn(1, 2),
        )
        pairs = [(r.model_id, r.check_num) for r in result]
        assert pairs == sorted(pairs)

    def test_returns_histogram_row_instances(self) -> None:
        result = bucket_failures(
            FIXTURES / "informants_qa.jsonl",
            run_checks_fn=_make_check_fn(7),
        )
        for row in result:
            assert isinstance(row, HistogramRow)
            assert isinstance(row.model_id, str)
            assert isinstance(row.check_num, int)
            assert isinstance(row.count, int)
            assert row.count >= 1

    def test_exception_in_check_fn_skips_record(self, tmp_path: Path) -> None:
        """A check_fn that raises should cause that record to be skipped, not crash."""
        # Single valid record
        informants = tmp_path / "informants.jsonl"
        informants.write_text(
            (FIXTURES / "informants_qa.jsonl").read_text(encoding="utf-8"),
            encoding="utf-8",
        )

        call_count = [0]

        def exploding_fn(record: Any, all_records: Any = None) -> list[Any]:
            call_count[0] += 1
            if call_count[0] == 1:
                raise RuntimeError("injected error")
            return []

        # Should not raise even though the first call raises
        result = bucket_failures(informants, run_checks_fn=exploding_fn)
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# Real run_record_checks via importlib (integration path)
# ---------------------------------------------------------------------------


class TestRealRunRecordChecks:
    """Integration path: load run_record_checks from scripts/ via importlib.

    This test skips if scripts/qa_check.py is not present (e.g. in a
    trimmed CI environment). In the normal development environment it
    exercises the importlib load path end-to-end.
    """

    def test_bucket_failures_with_real_checks(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        qa_path = repo_root / "scripts" / "qa_check.py"
        if not qa_path.exists():
            pytest.skip("scripts/qa_check.py not found")

        result = bucket_failures(
            FIXTURES / "informants_qa.jsonl",
            repo_root=repo_root,
        )
        # qa-004 has 5 items, which should fail check_1.
        # The function must return HistogramRow objects with check_num=1.
        assert isinstance(result, list)
        check1_rows = [r for r in result if r.check_num == 1]
        assert len(check1_rows) >= 1, (
            "Expected check_1 failure for qa-004 (5 items < 10 threshold)"
        )
        row = check1_rows[0]
        assert row.model_id == "test-model-a"
        assert row.count == 1
