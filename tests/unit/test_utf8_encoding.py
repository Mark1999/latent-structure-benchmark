"""UTF-8 encoding round-trip test for the JSONL writer path.

Acceptance criterion F2-T06: writing a record containing non-ASCII
characters (U+02BC, U+0131, U+014D, U+1EBF) must not raise a codec
error, and the bytes read back must be identical to what was written.
"""

from __future__ import annotations

import json
import tempfile
from datetime import datetime
from pathlib import Path

from cdb_collect.jsonl import append_failure, append_record, read_records
from cdb_core import (
    FreelistRecord,
    InformantRecord,
    InterviewRecord,
    PileSortRecord,
)

# The four characters that triggered cp1252 codec errors during the
# 2026-04-20 shakedown (holidays domain).
#   U+02BC  MODIFIER LETTER APOSTROPHE      (e.g., Norouz→Nowruz notation)
#   U+0131  LATIN SMALL LETTER DOTLESS I    (Turkish)
#   U+014D  LATIN SMALL LETTER O WITH MACRON (e.g., Ōbon)
#   U+1EBF  LATIN SMALL LETTER E WITH CIRCUMFLEX AND ACUTE (Vietnamese)
NON_ASCII_ITEMS = [
    "nowr\u02bcuz",      # U+02BC
    "k\u0131rk",         # U+0131
    "\u014dbon",         # U+014D
    "t\u1ebft",          # U+1EBF
]


def _make_non_ascii_record() -> InformantRecord:
    """Build a minimal InformantRecord with non-ASCII items in the free list."""
    return InformantRecord(
        informant_id="utf8_test_01",
        domain_slug="holidays",
        run_index=0,
        collection_date=datetime(2026, 4, 20, 12, 0, 0),
        model_id="claude-opus-4-6",
        model_version_returned="claude-opus-4-6-20260401",
        family="claude",
        provider="anthropic",
        provider_request_id="msg_utf8test",
        knowledge_cutoff=None,
        open_weights=False,
        origin_country="us",
        alignment_method=None,
        collection_method="anthropic_api",
        collection_mode="single_pass",
        api_endpoint="https://api.anthropic.com/v1/messages",
        api_version="",
        temperature=0.7,
        top_p=None,
        max_tokens=16384,
        system_prompt="",
        freelist=FreelistRecord(
            prompt_verbatim="List holiday terms",
            prompt_version="v1",
            response_verbatim=" ".join(NON_ASCII_ITEMS),
            response_object_json={},
            input_tokens=10,
            output_tokens=20,
            latency_ms=500,
            stop_reason="end_turn",
            parsed_items=NON_ASCII_ITEMS,
            parsed_raw_order=NON_ASCII_ITEMS,
        ),
        pile_sort=PileSortRecord(
            prompt_verbatim="",
            prompt_version="v1",
            response_verbatim="",
            response_object_json={},
            input_tokens=0,
            output_tokens=0,
            latency_ms=0,
            stop_reason="not_collected",
            parsed_piles=[],
            parsed_matrix=[],
        ),
        interview=InterviewRecord(
            prompt_verbatim="",
            prompt_version="v1",
            response_verbatim="",
            response_object_json={},
            input_tokens=0,
            output_tokens=0,
            latency_ms=0,
            stop_reason="not_collected",
            parsed_pile_labels=[],
        ),
        sha256_manifest={
            "freelist_prompt": "a" * 64,
            "freelist_response": "b" * 64,
            "pilesort_prompt": "c" * 64,
            "pilesort_response": "d" * 64,
            "interview_prompt": "e" * 64,
            "interview_response": "f" * 64,
            "request_params": "0" * 64,
            "informant_record_total": "1" * 64,
        },
        qa_passed=True,
        qa_notes="",
    )


def test_non_ascii_round_trip_no_exception():
    """append_record + read_records must not raise on non-ASCII content."""
    record = _make_non_ascii_record()
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "test_utf8.jsonl"
        # Must not raise UnicodeEncodeError (was 'charmap' codec on Windows)
        append_record(record, path)

        records = read_records(path)
        assert len(records) == 1
        assert records[0].informant_id == "utf8_test_01"
        assert records[0].freelist.parsed_items == NON_ASCII_ITEMS


def test_non_ascii_byte_exact_round_trip():
    """Bytes written and bytes read back must be identical (UTF-8, no mojibake)."""
    record = _make_non_ascii_record()
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "test_utf8_bytes.jsonl"
        append_record(record, path)

        raw_bytes = path.read_bytes()
        # Verify the file is valid UTF-8
        decoded = raw_bytes.decode("utf-8")

        # Verify each non-ASCII code point survives the round-trip
        for item in NON_ASCII_ITEMS:
            assert item in decoded, (
                f"Item {item!r} not found in decoded JSONL — "
                "encoding may have been corrupted"
            )

        # Re-encode decoded text and confirm byte-exact identity
        assert decoded.encode("utf-8") == raw_bytes


def test_append_failure_non_ascii():
    """append_failure must handle non-ASCII in error messages without raising.

    json.dumps uses ensure_ascii=True by default, so U+02BC is written as
    the JSON escape sequence \\u02bc.  The file is still valid UTF-8 and the
    character survives the round-trip when the JSON is parsed back.
    """
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "failures.jsonl"
        error_msg = "codec error near \u02bc at position 4428"
        # Must not raise UnicodeEncodeError (was cp1252 on Windows)
        append_failure(
            ValueError(error_msg),
            {"model_id": "test-model", "domain": "holidays"},
            path,
        )
        raw_text = path.read_bytes().decode("utf-8")
        parsed = json.loads(raw_text.strip())
        # The character survives round-trip through json.loads
        assert "\u02bc" in parsed["error_message"]


def test_non_ascii_items_in_jsonl_are_valid_json():
    """Each line written by append_record must be parseable as JSON."""
    record = _make_non_ascii_record()
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "test_valid_json.jsonl"
        append_record(record, path)

        lines = path.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1
        parsed = json.loads(lines[0])
        assert parsed["freelist"]["parsed_items"] == NON_ASCII_ITEMS
