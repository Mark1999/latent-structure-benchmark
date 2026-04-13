"""Tests for cost_report.py."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from scripts.cost_report import report


def _write_fixture(path: Path) -> None:
    records = [
        {
            "collection_date": "2026-04-13T10:00:00",
            "model_id": "claude-opus-4-6",
            "domain_slug": "family",
            "freelist": {"input_tokens": 100, "output_tokens": 200},
            "pile_sort": {"input_tokens": 0, "output_tokens": 0},
            "interview": {"input_tokens": 0, "output_tokens": 0},
        },
        {
            "collection_date": "2026-04-14T10:00:00",
            "model_id": "claude-opus-4-6",
            "domain_slug": "family",
            "freelist": {"input_tokens": 150, "output_tokens": 250},
            "pile_sort": {"input_tokens": 0, "output_tokens": 0},
            "interview": {"input_tokens": 0, "output_tokens": 0},
        },
        {
            "collection_date": "2026-03-15T10:00:00",
            "model_id": "claude-opus-4-6",
            "domain_slug": "holidays",
            "freelist": {"input_tokens": 80, "output_tokens": 300},
            "pile_sort": {"input_tokens": 0, "output_tokens": 0},
            "interview": {"input_tokens": 0, "output_tokens": 0},
        },
    ]
    with open(path, "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


def test_report_current_month(capsys):
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "test.jsonl"
        _write_fixture(path)
        report(path, month="2026-04")

    captured = capsys.readouterr()
    assert "Records: 2" in captured.out
    assert "$" in captured.out


def test_report_all_time(capsys):
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "test.jsonl"
        _write_fixture(path)
        report(path, month="all")

    captured = capsys.readouterr()
    assert "Records: 3" in captured.out


def test_report_group_by_domain(capsys):
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "test.jsonl"
        _write_fixture(path)
        report(path, month="all", group_by="domain")

    captured = capsys.readouterr()
    assert "family" in captured.out
    assert "holidays" in captured.out


def test_report_empty(capsys):
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "empty.jsonl"
        path.touch()
        report(path, month="2026-04")

    captured = capsys.readouterr()
    assert "No records" in captured.out


def test_report_nonexistent(capsys):
    report(Path("/tmp/nonexistent_cost_report_test.jsonl"), month="2026-04")
    captured = capsys.readouterr()
    assert "No records" in captured.out
