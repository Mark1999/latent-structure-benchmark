"""Tests for scripts/build_db.py. Uses fixtures, no real API calls."""

from __future__ import annotations

import importlib.util
import json
import sqlite3
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "build_db", Path(__file__).resolve().parents[2] / "scripts" / "build_db.py",
)
_MOD = importlib.util.module_from_spec(_SPEC)  # type: ignore[arg-type]
_SPEC.loader.exec_module(_MOD)  # type: ignore[union-attr]
build_db = _MOD.build_db
_refuse_shakedown_path = _MOD._refuse_shakedown_path


def _make_record(
    informant_id: str = "abc123",
    run_index: int = 0,
    items: list[str] | None = None,
) -> dict:
    """Build a minimal valid InformantRecord dict."""
    if items is None:
        items = ["mother", "father", "sister", "brother"]

    matrix = [[1 if i == j else 0 for j in range(len(items))] for i in range(len(items))]
    # Put first two items in the same pile
    if len(items) >= 2:
        matrix[0][1] = 1
        matrix[1][0] = 1

    return {
        "informant_id": informant_id,
        "domain_slug": "family",
        "run_index": run_index,
        "collection_date": "2026-04-13T10:00:00Z",
        "collection_mode": "single_pass",
        "model_id": "claude-opus-4-6",
        "model_version_returned": "claude-opus-4-6-20260401",
        "family": "claude",
        "provider": "anthropic",
        "provider_request_id": "msg_test123",
        "knowledge_cutoff": None,
        "open_weights": False,
        "origin_country": "us",
        "alignment_method": "Constitutional AI",
        "collection_method": "anthropic_api",
        "api_endpoint": "https://api.anthropic.com/v1/messages",
        "api_version": "2023-06-01",
        "temperature": 0.7,
        "top_p": None,
        "max_tokens": 16384,
        "system_prompt": "You are a helpful assistant.",
        "freelist": {
            "prompt_verbatim": "List family terms.",
            "prompt_version": "v1",
            "response_verbatim": "1. mother\n2. father\n3. sister\n4. brother",
            "response_object_json": {},
            "input_tokens": 50,
            "output_tokens": 20,
            "latency_ms": 1200,
            "stop_reason": "end_turn",
            "parsed_items": items,
            "parsed_raw_order": items + ["cousin"],
        },
        "pile_sort": {
            "prompt_verbatim": "Sort these items.",
            "prompt_version": "v1",
            "response_verbatim": '{"piles":[["mother","father"],["sister","brother"]]}',
            "response_object_json": {},
            "input_tokens": 80,
            "output_tokens": 40,
            "latency_ms": 2000,
            "stop_reason": "end_turn",
            "parsed_piles": [items[:2], items[2:]],
            "parsed_matrix": matrix,
            "item_source": "own_freelist",
        },
        "interview": {
            "prompt_verbatim": "Name each pile.",
            "prompt_version": "v1",
            "response_verbatim": "1. Parents\n2. Siblings",
            "response_object_json": {},
            "input_tokens": 60,
            "output_tokens": 10,
            "latency_ms": 800,
            "stop_reason": "end_turn",
            "parsed_pile_labels": ["Parents", "Siblings"],
        },
        "sha256_manifest": {
            "freelist_prompt": "aaa",
            "freelist_response": "bbb",
            "pilesort_prompt": "ccc",
            "pilesort_response": "ddd",
            "interview_prompt": "eee",
            "interview_response": "fff",
            "request_params": "ggg",
            "informant_record_total": "hhh",
        },
        "qa_passed": True,
        "qa_notes": "",
    }


def test_build_db_creates_tables(tmp_path: Path):
    jsonl = tmp_path / "informants.jsonl"
    jsonl.write_text(json.dumps(_make_record()) + "\n")

    db = tmp_path / "lsb.sqlite"
    informant_count, decline_count = build_db(jsonl, db)

    assert informant_count == 1
    assert decline_count == 0
    assert db.exists()

    conn = sqlite3.connect(str(db))
    tables = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    assert "informants" in tables
    assert "freelist_items" in tables
    assert "pilesort_cells" in tables
    assert "interview_labels" in tables
    assert "decline_interviews" in tables
    conn.close()


def test_build_db_informant_row(tmp_path: Path):
    jsonl = tmp_path / "informants.jsonl"
    jsonl.write_text(json.dumps(_make_record()) + "\n")

    db = tmp_path / "lsb.sqlite"
    build_db(jsonl, db)

    conn = sqlite3.connect(str(db))
    row = conn.execute(
        "SELECT informant_id, model_id, qa_passed, open_weights FROM informants"
    ).fetchone()
    conn.close()

    assert row[0] == "abc123"
    assert row[1] == "claude-opus-4-6"
    assert row[2] == 1  # qa_passed = True → 1
    assert row[3] == 0  # open_weights = False → 0


def test_build_db_freelist_items(tmp_path: Path):
    jsonl = tmp_path / "informants.jsonl"
    jsonl.write_text(json.dumps(_make_record()) + "\n")

    db = tmp_path / "lsb.sqlite"
    build_db(jsonl, db)

    conn = sqlite3.connect(str(db))
    rows = conn.execute(
        "SELECT rank, item, is_truncated_in FROM freelist_items ORDER BY rank"
    ).fetchall()
    conn.close()

    # parsed_raw_order has 5 items, parsed_items has 4
    assert len(rows) == 5
    assert rows[0] == (0, "mother", 1)
    assert rows[4] == (4, "cousin", 0)  # not in parsed_items


def test_build_db_pilesort_cells(tmp_path: Path):
    jsonl = tmp_path / "informants.jsonl"
    jsonl.write_text(json.dumps(_make_record()) + "\n")

    db = tmp_path / "lsb.sqlite"
    build_db(jsonl, db)

    conn = sqlite3.connect(str(db))
    # mother and father should be in same pile
    same = conn.execute(
        "SELECT in_same_pile FROM pilesort_cells "
        "WHERE item_a='mother' AND item_b='father'"
    ).fetchone()
    # mother and sister should not be in same pile
    diff = conn.execute(
        "SELECT in_same_pile FROM pilesort_cells "
        "WHERE item_a='mother' AND item_b='sister'"
    ).fetchone()
    conn.close()

    assert same[0] == 1
    assert diff[0] == 0


def test_build_db_interview_labels(tmp_path: Path):
    jsonl = tmp_path / "informants.jsonl"
    jsonl.write_text(json.dumps(_make_record()) + "\n")

    db = tmp_path / "lsb.sqlite"
    build_db(jsonl, db)

    conn = sqlite3.connect(str(db))
    rows = conn.execute(
        "SELECT pile_index, label FROM interview_labels ORDER BY pile_index"
    ).fetchall()
    conn.close()

    assert rows == [(0, "Parents"), (1, "Siblings")]


def test_build_db_multiple_records(tmp_path: Path):
    jsonl = tmp_path / "informants.jsonl"
    lines = [
        json.dumps(_make_record(informant_id="rec1", run_index=0)),
        json.dumps(_make_record(informant_id="rec2", run_index=1)),
        json.dumps(_make_record(informant_id="rec3", run_index=2)),
    ]
    jsonl.write_text("\n".join(lines) + "\n")

    db = tmp_path / "lsb.sqlite"
    informant_count, _ = build_db(jsonl, db)

    assert informant_count == 3

    conn = sqlite3.connect(str(db))
    n = conn.execute("SELECT COUNT(*) FROM informants").fetchone()[0]
    conn.close()
    assert n == 3


def test_build_db_skips_bad_json(tmp_path: Path):
    jsonl = tmp_path / "informants.jsonl"
    jsonl.write_text(
        json.dumps(_make_record()) + "\n"
        "this is not json\n"
    )

    db = tmp_path / "lsb.sqlite"
    informant_count, _ = build_db(jsonl, db)

    assert informant_count == 1


def test_build_db_nonexistent_jsonl(tmp_path: Path):
    db = tmp_path / "lsb.sqlite"
    informant_count, decline_count = build_db(tmp_path / "nope.jsonl", db)
    assert informant_count == 0
    assert decline_count == 0
    assert not db.exists()


def test_build_db_replaces_existing(tmp_path: Path):
    jsonl = tmp_path / "informants.jsonl"
    jsonl.write_text(json.dumps(_make_record()) + "\n")
    db = tmp_path / "lsb.sqlite"

    # Build once
    build_db(jsonl, db)
    # Build again — should replace, not append
    informant_count, _ = build_db(jsonl, db)

    assert informant_count == 1
    conn = sqlite3.connect(str(db))
    n = conn.execute("SELECT COUNT(*) FROM informants").fetchone()[0]
    conn.close()
    assert n == 1


# ── Shakedown refusal — docs/SHAKEDOWN_PROTOCOL.md §2 ──────────────────

class TestShakedownRefusal:
    """build_db refuses to canonicalize shakedown data (fourth labeling layer)."""

    def test_refuses_shakedown_path_build(self, tmp_path: Path):
        shakedown_dir = tmp_path / "data" / "shakedown" / "shakedown-2026-04-20"
        shakedown_dir.mkdir(parents=True)
        jsonl = shakedown_dir / "informants.jsonl"
        jsonl.write_text(json.dumps(_make_record()) + "\n")
        db = tmp_path / "lsb.sqlite"

        with pytest.raises(ValueError, match="shakedown"):
            build_db(jsonl, db)

        # Critically, no DB was written
        assert not db.exists()

    def test_refuses_shakedown_path_helper(self, tmp_path: Path):
        """Unit test of the _refuse_shakedown_path helper directly."""
        shakedown = tmp_path / "data" / "shakedown" / "informants.jsonl"
        shakedown.parent.mkdir(parents=True)
        shakedown.touch()
        with pytest.raises(ValueError, match="shakedown"):
            _refuse_shakedown_path(shakedown)

    def test_allows_non_shakedown_path(self, tmp_path: Path):
        """The helper does not raise on canonical paths."""
        canonical = tmp_path / "data" / "raw" / "informants.jsonl"
        canonical.parent.mkdir(parents=True)
        canonical.touch()
        # Should not raise
        _refuse_shakedown_path(canonical)
