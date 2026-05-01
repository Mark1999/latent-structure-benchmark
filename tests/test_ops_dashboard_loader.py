"""Tests for apps/ops_dashboard/lib/loader.py.

All tests use synthetic InformantRecord / DeclineInterview fixtures constructed
in-memory or written to a tmp_path JSONL file. No real API calls. No reads
from data/raw/informants.jsonl or data/raw/decline_interviews.jsonl.

Augmented (OPS-T4 tester pass):
- TestLoadDeclineInterviews: valid JSONL parse, cost_usd extra-field tolerance,
  malformed-line error (coverage points #18, #19, #20).
- TestLoadJsonlDicts: plain-dict return, empty/missing file (points #21, #22).

See ARCHITECTURE.md §3.2 (InformantRecord / DeclineInterview schemas) and
docs/DATA_DICTIONARY.md §1.1 / §10 for field semantics.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest
from cdb_core.schemas import (
    DeclineInterview,
    FreelistRecord,
    InformantRecord,
    InterviewRecord,
    PileSortRecord,
)

from apps.ops_dashboard.lib.loader import (
    filter_records,
    index_by_domain,
    index_by_model_id,
    index_by_run_id,
    load_decline_interviews,
    load_informants,
    load_jsonl_dicts,
)

# ── Shared manifest keys (DATA_DICTIONARY.md §1.1 — eight required keys) ──

_MANIFEST_KEYS = [
    "freelist_prompt",
    "freelist_response",
    "pilesort_prompt",
    "pilesort_response",
    "interview_prompt",
    "interview_response",
    "request_params",
    "informant_record_total",
]


# ── Record-builder helpers ──

def _freelist_record() -> FreelistRecord:
    return FreelistRecord(
        prompt_verbatim="List every family term you can think of.",
        prompt_version="v1",
        response_verbatim="1. mother\n2. father\n3. sister",
        response_object_json={"id": "msg_001"},
        input_tokens=50,
        output_tokens=20,
        latency_ms=900,
        stop_reason="end_turn",
        parsed_items=["mother", "father", "sister"],
        parsed_raw_order=["mother", "father", "sister"],
    )


def _pilesort_record() -> PileSortRecord:
    return PileSortRecord(
        prompt_verbatim="Sort these items into piles.",
        prompt_version="v1",
        response_verbatim="Pile 1: mother, father\nPile 2: sister",
        response_object_json={"id": "msg_002"},
        input_tokens=60,
        output_tokens=30,
        latency_ms=1100,
        stop_reason="end_turn",
        parsed_piles=[["mother", "father"], ["sister"]],
        parsed_matrix=[[1, 1, 0], [1, 1, 0], [0, 0, 1]],
    )


def _interview_record() -> InterviewRecord:
    return InterviewRecord(
        prompt_verbatim="Name each pile.",
        prompt_version="v1",
        response_verbatim="Pile 1: Parents\nPile 2: Siblings",
        response_object_json={"id": "msg_003"},
        input_tokens=40,
        output_tokens=15,
        latency_ms=700,
        stop_reason="end_turn",
        parsed_pile_labels=["Parents", "Siblings"],
    )


def _make_record(
    *,
    informant_id: str = "aaaa0000bbbb1111",
    domain_slug: str = "family",
    model_id: str = "claude-opus-4-6",
    run_index: int = 0,
    qa_passed: bool = True,
) -> InformantRecord:
    """Construct a minimal but fully valid InformantRecord for testing."""
    return InformantRecord(
        informant_id=informant_id,
        domain_slug=domain_slug,
        run_index=run_index,
        collection_date=datetime(2026, 5, 1, 10, 0, 0),
        model_id=model_id,
        model_version_returned=f"{model_id}-20260501",
        family=model_id.split("-")[0],
        provider="anthropic",
        provider_request_id=f"req_{informant_id}",
        knowledge_cutoff=None,
        open_weights=False,
        origin_country="us",
        alignment_method=None,
        collection_method="anthropic_api",
        api_endpoint="https://api.anthropic.com/v1/messages",
        api_version="2023-06-01",
        temperature=0.7,
        top_p=None,
        max_tokens=4096,
        system_prompt="You are participating in a cognitive anthropology study.",
        freelist=_freelist_record(),
        pile_sort=_pilesort_record(),
        interview=_interview_record(),
        sha256_manifest={k: "0" * 64 for k in _MANIFEST_KEYS},
        qa_passed=qa_passed,
    )


def _write_jsonl(path: Path, records: list[InformantRecord]) -> None:
    """Serialize records to a JSONL file at path (test helper only)."""
    with path.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(rec.model_dump_json() + "\n")


# ── Fixtures ──

@pytest.fixture()
def three_records() -> list[InformantRecord]:
    """Three distinct InformantRecord objects for loader tests."""
    return [
        _make_record(
            informant_id="rec0000000000001",
            domain_slug="family",
            model_id="claude-opus-4-6",
            run_index=0,
        ),
        _make_record(
            informant_id="rec0000000000002",
            domain_slug="holidays",
            model_id="gpt-4o",
            run_index=0,
        ),
        _make_record(
            informant_id="rec0000000000003",
            domain_slug="family",
            model_id="gpt-4o",
            run_index=1,
        ),
    ]


@pytest.fixture()
def five_records() -> list[InformantRecord]:
    """Five records spanning two models and three domains."""
    return [
        _make_record(
            informant_id="r00000000000001",
            domain_slug="family",
            model_id="claude-opus-4-6",
            run_index=0,
        ),
        _make_record(
            informant_id="r00000000000002",
            domain_slug="holidays",
            model_id="claude-opus-4-6",
            run_index=0,
        ),
        _make_record(
            informant_id="r00000000000003",
            domain_slug="family",
            model_id="gpt-4o",
            run_index=0,
        ),
        _make_record(
            informant_id="r00000000000004",
            domain_slug="food",
            model_id="gpt-4o",
            run_index=0,
        ),
        _make_record(
            informant_id="r00000000000005",
            domain_slug="food",
            model_id="claude-opus-4-6",
            run_index=1,
        ),
    ]


# ── load_informants ──

class TestLoadInformants:
    def test_loads_valid_jsonl(
        self, tmp_path: Path, three_records: list[InformantRecord]
    ) -> None:
        """Parses a valid 3-row JSONL file and returns InformantRecord instances."""
        jsonl_file = tmp_path / "informants.jsonl"
        _write_jsonl(jsonl_file, three_records)

        result = load_informants(jsonl_file)

        assert len(result) == 3
        assert all(isinstance(r, InformantRecord) for r in result)
        assert result[0].informant_id == "rec0000000000001"
        assert result[1].domain_slug == "holidays"
        assert result[2].model_id == "gpt-4o"

    def test_empty_file_returns_empty_list(self, tmp_path: Path) -> None:
        """An empty JSONL file returns an empty list without raising."""
        jsonl_file = tmp_path / "informants.jsonl"
        jsonl_file.write_text("", encoding="utf-8")

        result = load_informants(jsonl_file)

        assert result == []

    def test_blank_lines_are_skipped(
        self, tmp_path: Path, three_records: list[InformantRecord]
    ) -> None:
        """Blank lines inside the JSONL are skipped without error."""
        jsonl_file = tmp_path / "informants.jsonl"
        lines = [r.model_dump_json() for r in three_records]
        content = "\n".join(lines[:1]) + "\n\n" + "\n".join(lines[1:]) + "\n"
        jsonl_file.write_text(content, encoding="utf-8")

        result = load_informants(jsonl_file)

        assert len(result) == 3

    def test_malformed_json_raises_with_line_number(
        self, tmp_path: Path, three_records: list[InformantRecord]
    ) -> None:
        """A line with invalid JSON raises ValueError naming the line number."""
        jsonl_file = tmp_path / "informants.jsonl"
        good_line = three_records[0].model_dump_json()
        bad_line = '{"informant_id": "bad", INVALID JSON}'
        jsonl_file.write_text(good_line + "\n" + bad_line + "\n", encoding="utf-8")

        with pytest.raises(ValueError, match=r"line 2"):
            load_informants(jsonl_file)

    def test_schema_validation_error_raises_with_line_number(
        self, tmp_path: Path
    ) -> None:
        """A line with valid JSON but missing required fields raises ValueError."""
        jsonl_file = tmp_path / "informants.jsonl"
        bad_obj = {"informant_id": "partial", "domain_slug": "family"}
        jsonl_file.write_text(json.dumps(bad_obj) + "\n", encoding="utf-8")

        with pytest.raises(ValueError, match=r"line 1"):
            load_informants(jsonl_file)

    def test_round_trip_preserves_values(
        self, tmp_path: Path, three_records: list[InformantRecord]
    ) -> None:
        """Field values survive the JSONL write → load round-trip."""
        jsonl_file = tmp_path / "informants.jsonl"
        _write_jsonl(jsonl_file, three_records)

        result = load_informants(jsonl_file)

        for original, loaded in zip(three_records, result, strict=True):
            assert loaded.informant_id == original.informant_id
            assert loaded.domain_slug == original.domain_slug
            assert loaded.model_id == original.model_id


# ── index_by_run_id ──

class TestIndexByRunId:
    def test_returns_dict_keyed_by_informant_id(
        self, three_records: list[InformantRecord]
    ) -> None:
        """Keys in the returned dict are informant_id values."""
        index = index_by_run_id(three_records)

        assert set(index.keys()) == {
            "rec0000000000001",
            "rec0000000000002",
            "rec0000000000003",
        }

    def test_round_trip_lookup(self, three_records: list[InformantRecord]) -> None:
        """Looking up a known informant_id returns the correct record."""
        index = index_by_run_id(three_records)

        rec = index["rec0000000000002"]
        assert rec.domain_slug == "holidays"
        assert rec.model_id == "gpt-4o"

    def test_duplicate_informant_id_raises(
        self, three_records: list[InformantRecord]
    ) -> None:
        """Duplicate informant_id raises ValueError (append-only contract violation)."""
        duplicate = _make_record(informant_id="rec0000000000001")  # same as first
        records_with_dup = [*three_records, duplicate]

        with pytest.raises(ValueError, match="rec0000000000001"):
            index_by_run_id(records_with_dup)

    def test_empty_list_returns_empty_dict(self) -> None:
        """Empty input returns empty dict without error."""
        assert index_by_run_id([]) == {}


# ── index_by_model_id ──

class TestIndexByModelId:
    def test_keys_are_model_ids(self, five_records: list[InformantRecord]) -> None:
        """Dict keys are the distinct model_id values in the input."""
        index = index_by_model_id(five_records)

        assert set(index.keys()) == {"claude-opus-4-6", "gpt-4o"}

    def test_lists_contain_correct_records(
        self, five_records: list[InformantRecord]
    ) -> None:
        """Each list contains records with the matching model_id."""
        index = index_by_model_id(five_records)

        for model_id, recs in index.items():
            assert all(r.model_id == model_id for r in recs)

    def test_list_lengths_are_correct(
        self, five_records: list[InformantRecord]
    ) -> None:
        """Count of records per model matches expectation."""
        index = index_by_model_id(five_records)

        assert len(index["claude-opus-4-6"]) == 3  # r1, r2, r5
        assert len(index["gpt-4o"]) == 2            # r3, r4

    def test_empty_list_returns_empty_dict(self) -> None:
        assert index_by_model_id([]) == {}


# ── index_by_domain ──

class TestIndexByDomain:
    def test_keys_are_domain_slugs(self, five_records: list[InformantRecord]) -> None:
        index = index_by_domain(five_records)

        assert set(index.keys()) == {"family", "holidays", "food"}

    def test_lists_contain_correct_records(
        self, five_records: list[InformantRecord]
    ) -> None:
        index = index_by_domain(five_records)

        for domain, recs in index.items():
            assert all(r.domain_slug == domain for r in recs)

    def test_list_lengths_are_correct(
        self, five_records: list[InformantRecord]
    ) -> None:
        index = index_by_domain(five_records)

        assert len(index["family"]) == 2    # r1, r3
        assert len(index["holidays"]) == 1  # r2
        assert len(index["food"]) == 2      # r4, r5

    def test_empty_list_returns_empty_dict(self) -> None:
        assert index_by_domain([]) == {}


# ── filter_records ──

class TestFilterRecords:
    def test_no_filters_returns_all(
        self, five_records: list[InformantRecord]
    ) -> None:
        """Both None → every record is returned."""
        result = filter_records(five_records)

        assert result == five_records

    def test_filter_by_model_id(self, five_records: list[InformantRecord]) -> None:
        result = filter_records(five_records, model_id="gpt-4o")

        assert len(result) == 2
        assert all(r.model_id == "gpt-4o" for r in result)

    def test_filter_by_domain(self, five_records: list[InformantRecord]) -> None:
        result = filter_records(five_records, domain="food")

        assert len(result) == 2
        assert all(r.domain_slug == "food" for r in result)

    def test_filter_by_model_and_domain(
        self, five_records: list[InformantRecord]
    ) -> None:
        """Both filters ANDed — only records matching both are returned."""
        result = filter_records(
            five_records, model_id="claude-opus-4-6", domain="family"
        )

        assert len(result) == 1
        assert result[0].informant_id == "r00000000000001"

    def test_filter_no_match_returns_empty(
        self, five_records: list[InformantRecord]
    ) -> None:
        result = filter_records(five_records, model_id="nonexistent-model")

        assert result == []

    def test_filter_does_not_mutate_input(
        self, five_records: list[InformantRecord]
    ) -> None:
        """filter_records returns a new list; input list is unchanged."""
        original_len = len(five_records)
        filter_records(five_records, model_id="gpt-4o")

        assert len(five_records) == original_len

    def test_empty_input_returns_empty(self) -> None:
        result = filter_records([], model_id="gpt-4o", domain="family")

        assert result == []


# ── DeclineInterview builder ──────────────────────────────────────────────────

def _make_decline_interview(
    *,
    decline_interview_id: str = "dec_loader_001",
    originating_informant_id: str = "aaaa0000bbbb1111",
    originating_step: str = "freelist",
    originating_outcome_class: str = "refusal_string_match",
    response_verbatim: str = "I cannot help with that.",
) -> DeclineInterview:
    """Minimal valid DeclineInterview for loader tests."""
    return DeclineInterview(
        decline_interview_id=decline_interview_id,
        originating_informant_id=originating_informant_id,
        originating_failure_id=None,
        originating_step=originating_step,  # type: ignore[arg-type]
        originating_outcome_class=originating_outcome_class,  # type: ignore[arg-type]
        detection_rule_version="v1",
        detection_timestamp=datetime(2026, 5, 1, 10, 0, 0),
        followup_timestamp=datetime(2026, 5, 1, 10, 1, 0),
        model_id="fixture-model-001",
        model_version_returned="fixture-model-001-20260501",
        provider="fixture_provider",
        api_endpoint="https://api.fixture.invalid/v1/messages",
        prompt_version="decline_v1",
        sha256_manifest="b" * 64,
        prompt_verbatim="Describe what happened in that exchange.",
        response_verbatim=response_verbatim,
        input_tokens=50,
        output_tokens=30,
        latency_ms=800,
        stop_reason="stop",
    )


def _write_decline_interviews_jsonl(
    path: Path, records: list[DeclineInterview]
) -> None:
    """Serialize DeclineInterview records to a JSONL file (test helper)."""
    with path.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(rec.model_dump_json() + "\n")


# ── load_decline_interviews ───────────────────────────────────────────────────


class TestLoadDeclineInterviews:
    def test_loads_valid_jsonl(self, tmp_path: Path) -> None:
        """Valid JSONL with two DeclineInterview rows parses to two objects.
        Coverage point #18."""
        records = [
            _make_decline_interview(
                decline_interview_id="dec_load_01",
                originating_informant_id="inf0000000000001",
                response_verbatim="First decline.",
            ),
            _make_decline_interview(
                decline_interview_id="dec_load_02",
                originating_informant_id="inf0000000000002",
                response_verbatim="Second decline.",
            ),
        ]
        jsonl_file = tmp_path / "decline_interviews.jsonl"
        _write_decline_interviews_jsonl(jsonl_file, records)

        result = load_decline_interviews(jsonl_file)

        assert len(result) == 2
        assert all(isinstance(r, DeclineInterview) for r in result)
        assert result[0].decline_interview_id == "dec_load_01"
        assert result[1].originating_informant_id == "inf0000000000002"

    def test_missing_file_returns_empty_list(self, tmp_path: Path) -> None:
        """A missing file returns an empty list without raising (normal first-class
        state — no decline data collected yet)."""
        path = tmp_path / "decline_interviews.jsonl"
        assert not path.exists()
        result = load_decline_interviews(path)
        assert result == []

    def test_empty_file_returns_empty_list(self, tmp_path: Path) -> None:
        """An empty JSONL file returns an empty list."""
        jsonl_file = tmp_path / "decline_interviews.jsonl"
        jsonl_file.write_text("", encoding="utf-8")
        result = load_decline_interviews(jsonl_file)
        assert result == []

    def test_tolerates_extra_cost_usd_field(self, tmp_path: Path) -> None:
        """Legacy records carrying a cost_usd field are parsed without error.

        DeclineInterview uses Pydantic v2 default (extra='ignore'), so unknown
        fields are silently dropped.  This test is a regression guard for the
        schema-strip task that removed cost_usd (F2-T13).

        Coverage point #19.
        """
        di = _make_decline_interview(decline_interview_id="dec_cost_01")
        # Inject the legacy field into the serialised dict
        as_dict = json.loads(di.model_dump_json())
        as_dict["cost_usd"] = 0.00042  # field removed in F2-T13
        jsonl_file = tmp_path / "decline_interviews.jsonl"
        jsonl_file.write_text(json.dumps(as_dict) + "\n", encoding="utf-8")

        result = load_decline_interviews(jsonl_file)

        assert len(result) == 1
        assert result[0].decline_interview_id == "dec_cost_01"
        assert not hasattr(result[0], "cost_usd")

    def test_malformed_line_raises_with_line_number(self, tmp_path: Path) -> None:
        """A line with invalid JSON raises ValueError naming the 1-indexed line
        number.  Coverage point #20."""
        di = _make_decline_interview(decline_interview_id="dec_malf_good")
        good_line = di.model_dump_json()
        bad_line = '{"decline_interview_id": "broken", INVALID JSON}'
        jsonl_file = tmp_path / "decline_interviews.jsonl"
        jsonl_file.write_text(
            good_line + "\n" + bad_line + "\n", encoding="utf-8"
        )

        with pytest.raises(ValueError, match=r"line 2"):
            load_decline_interviews(jsonl_file)


# ── load_jsonl_dicts ──────────────────────────────────────────────────────────


class TestLoadJsonlDicts:
    def test_returns_plain_dicts(self, tmp_path: Path) -> None:
        """Each line is parsed to a plain dict (no Pydantic coercion).
        Coverage point #21."""
        rows = [
            {"decline_interview_id": "d001", "manual_classification": "k_frame"},
            {"decline_interview_id": "d002", "manual_classification": "k_vocab"},
        ]
        jsonl_file = tmp_path / "manual_classification.jsonl"
        with jsonl_file.open("w") as fh:
            for row in rows:
                fh.write(json.dumps(row) + "\n")

        result = load_jsonl_dicts(jsonl_file)

        assert len(result) == 2
        assert all(isinstance(r, dict) for r in result)
        assert result[0]["decline_interview_id"] == "d001"
        assert result[1]["manual_classification"] == "k_vocab"

    def test_empty_file_returns_empty_list(self, tmp_path: Path) -> None:
        """An empty file returns an empty list.  Coverage point #22."""
        jsonl_file = tmp_path / "empty.jsonl"
        jsonl_file.write_text("", encoding="utf-8")
        assert load_jsonl_dicts(jsonl_file) == []

    def test_missing_file_returns_empty_list(self, tmp_path: Path) -> None:
        """A missing file returns an empty list (caller need not check existence).
        Coverage point #22."""
        path = tmp_path / "nonexistent.jsonl"
        assert not path.exists()
        assert load_jsonl_dicts(path) == []

    def test_malformed_line_raises_with_line_number(self, tmp_path: Path) -> None:
        """A line with invalid JSON raises ValueError naming the line number."""
        jsonl_file = tmp_path / "broken.jsonl"
        jsonl_file.write_text(
            '{"ok": 1}\n' + "NOT JSON AT ALL\n", encoding="utf-8"
        )
        with pytest.raises(ValueError, match=r"line 2"):
            load_jsonl_dicts(jsonl_file)

    def test_blank_lines_are_skipped(self, tmp_path: Path) -> None:
        """Blank lines within the file are skipped without error."""
        jsonl_file = tmp_path / "with_blanks.jsonl"
        jsonl_file.write_text(
            '{"x": 1}\n\n{"x": 2}\n', encoding="utf-8"
        )
        result = load_jsonl_dicts(jsonl_file)
        assert len(result) == 2
