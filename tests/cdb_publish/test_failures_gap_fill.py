"""Gap-fill tests for cdb_publish.failures and cdb_publish.sanitize.

Covers specific regression risks identified in the Tester gap analysis for
Phase 6 T9. Tester verdict: docs/status/2026-05-12-phase6-T9-tester-verdict.md

No real API calls. All tests use synthetic fixtures in
tests/fixtures/failures/ or written to tmp_path.
See CLAUDE.md §6 R9 (no real API in tests).

Gaps filled:
1. framing_note verbatim regression — exact §5.1 CDA SME text (not just len > 50).
2. sk- regex pattern literal assertion (the pattern string itself).
3. 49-char sk- NOT redacted (boundary: exactly one below the 50-char minimum).
4. DATA_DICTIONARY.md §5.2 anti-attribution sentence present.
5. DATA_DICTIONARY.md §5.5 provider-quote advisory present.
6. Published JSON API-key leak regression (load output file, grep for patterns).
7. originating_outcome_class all 7 enum values round-trip verbatim.
8. cost_usd intentionally absent from published records.
9. Manifest Pydantic schema failures field round-trips.
10. PublishedFailuresFile Pydantic validation of output (acceptance criterion 3).
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

# ---------------------------------------------------------------------------
# Fixtures path
# ---------------------------------------------------------------------------

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "failures"
DATA_DICTIONARY_PATH = Path(__file__).parent.parent.parent / "docs" / "DATA_DICTIONARY.md"


def _copy_fixtures(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Copy fixture JSONL files to tmp_path. Returns (failures, di, informants)."""
    failures = tmp_path / "failures.jsonl"
    di = tmp_path / "decline_interviews.jsonl"
    informants = tmp_path / "informants.jsonl"
    shutil.copy(FIXTURES_DIR / "failures.jsonl", failures)
    shutil.copy(FIXTURES_DIR / "decline_interviews.jsonl", di)
    shutil.copy(FIXTURES_DIR / "informants.jsonl", informants)
    return failures, di, informants


# ---------------------------------------------------------------------------
# 1. framing_note verbatim regression
# ---------------------------------------------------------------------------


class TestFramingNoteVerbatim:
    """Assert framing_note is exactly the CDA SME §5.1 text — guards against
    inadvertent paraphrase in future edits.
    """

    # Verbatim text required by CDA SME §5.1. This copy is the regression anchor.
    _EXPECTED_FRAMING_NOTE = (
        "These records preserve verbatim outputs from collection sessions that did "
        "not produce a parseable primary-step response. Each record is a property "
        "of the LSB collection pipeline's output distribution, not a claim about "
        "the model's intent or state-of-mind. The `originating_outcome_class` field "
        "names the LSB-side detection rule (e.g., `refusal_string_match` describes "
        "a string-pattern match by the LSB pipeline, not a model decision to refuse). "
        "See the methodology page for the failures-as-findings framing."
    )

    def test_framing_note_module_constant_verbatim(self) -> None:
        """The _FRAMING_NOTE constant in failures.py equals the CDA SME §5.1 text."""
        from cdb_publish.failures import _FRAMING_NOTE

        assert _FRAMING_NOTE == self._EXPECTED_FRAMING_NOTE, (
            "failures.py _FRAMING_NOTE has drifted from CDA SME §5.1 required text. "
            "Do not paraphrase — see docs/status/2026-05-12-phase6-T9-cda-sme-verdict.md §5.1."
        )

    def test_framing_note_in_published_file_verbatim(self, tmp_path: Path) -> None:
        """The framing_note field in emitted JSON equals the CDA SME §5.1 text."""
        from cdb_publish.failures import build_failures

        failures_path, di_path, inf_path = _copy_fixtures(tmp_path)
        out = tmp_path / "out"

        build_failures(
            raw_failures_path=failures_path,
            raw_decline_interviews_path=di_path,
            raw_informants_path=inf_path,
            output_dir=out,
            domain_slugs=["family"],
        )

        family_json = json.loads((out / "family.json").read_text())
        assert family_json["framing_note"] == self._EXPECTED_FRAMING_NOTE, (
            "Published framing_note in family.json does not match CDA SME §5.1 verbatim text."
        )


# ---------------------------------------------------------------------------
# 2. sk- regex pattern literal assertion
# ---------------------------------------------------------------------------


class TestSkRegexPatternShape:
    """Assert the generic sk- regex uses the CDA SME §5.4 required pattern:
    word-boundary anchored, minimum 50 chars. Tests the regex itself, not just
    behavior, to prevent future pattern-shape drift.
    """

    def test_generic_sk_pattern_is_word_boundary_anchored_50_min(self) -> None:
        """The generic sk- pattern in _API_KEY_PATTERNS uses \\bsk-[a-zA-Z0-9_-]{50,}."""
        from cdb_publish.sanitize import _API_KEY_PATTERNS

        # Find the generic sk- pattern (not sk-ant- and not sk-or-v1-).
        generic_patterns = [
            p for p in _API_KEY_PATTERNS
            if (
                p.pattern.startswith(r"\bsk-")
                and "ant" not in p.pattern
                and "or-v1" not in p.pattern
            )
        ]
        assert len(generic_patterns) == 1, (
            f"Expected exactly one generic sk- pattern in _API_KEY_PATTERNS, "
            f"got {len(generic_patterns)}: {[p.pattern for p in generic_patterns]}"
        )
        assert generic_patterns[0].pattern == r"\bsk-[a-zA-Z0-9_-]{50,}", (
            f"Generic sk- pattern is '{generic_patterns[0].pattern}', "
            f"expected '\\bsk-[a-zA-Z0-9_-]{{50,}}' per CDA SME §5.4."
        )


# ---------------------------------------------------------------------------
# 3. 49-char sk- NOT redacted (one below minimum boundary)
# ---------------------------------------------------------------------------


class TestSkRegexBoundary:
    """Test the exact 50-char minimum boundary of the generic sk- regex.

    The Coder's test_api_key_generic_sk_short_not_matched uses 20 chars.
    This test probes the exact boundary: 49 chars is NOT redacted, 50 is.
    """

    def test_sk_49_chars_not_redacted(self) -> None:
        """A 49-char sk- token (one below minimum) is NOT redacted."""
        from cdb_publish.sanitize import sanitize_for_publication

        token_49 = "sk-" + "E" * 49
        result = sanitize_for_publication(f"Token: {token_49}")
        assert token_49 in result, (
            "sk- token with 49 chars after 'sk-' was unexpectedly redacted. "
            "CDA SME §5.4 requires minimum 50 chars."
        )
        assert "[redacted" not in result

    def test_sk_50_chars_is_redacted(self) -> None:
        """A 50-char sk- token (at minimum) IS redacted."""
        from cdb_publish.sanitize import sanitize_for_publication

        token_50 = "sk-" + "F" * 50
        result = sanitize_for_publication(f"Token: {token_50}")
        assert token_50 not in result, (
            "sk- token with exactly 50 chars after 'sk-' was NOT redacted. "
            "CDA SME §5.4 requires minimum 50 chars."
        )
        assert "[redacted: secret pattern]" in result


# ---------------------------------------------------------------------------
# 4 + 5. DATA_DICTIONARY.md static text scans
# ---------------------------------------------------------------------------


class TestDataDictionaryStaticText:
    """Assert that DATA_DICTIONARY.md §12 contains the two binding text
    passages required by CDA SME §5.2 and §5.5. These are regression tests
    against future doc drift — if the text is removed or paraphrased, the
    tests fail.
    """

    def test_data_dictionary_anti_attribution_sentence_present(self) -> None:
        """CDA SME §5.2 binding sentence is in DATA_DICTIONARY.md §12.

        Required verbatim per verdict: 'Each enum value names the LSB-side
        detection rule ... The enum values do not attribute intent, belief,
        or state-of-mind to the model.'
        """
        text = DATA_DICTIONARY_PATH.read_text(encoding="utf-8")
        # Check for the two key clauses that must appear together in §12.
        assert "Each enum value names the LSB-side" in text, (
            "DATA_DICTIONARY.md is missing the §5.2 anti-attribution opening clause "
            "('Each enum value names the LSB-side ...')."
        )
        assert "do not attribute intent, belief, or state-of-mind to the model" in text, (
            "DATA_DICTIONARY.md is missing the §5.2 anti-attribution sentence "
            "('The enum values do not attribute intent, belief, or state-of-mind to the model')."
        )
        # Confirm these appear inside the §12 section (after the section header).
        section_start = text.find("## 12. Published failures JSON shape")
        assert section_start != -1, "DATA_DICTIONARY.md §12 section not found."
        section_text = text[section_start:]
        assert "Each enum value names the LSB-side" in section_text
        assert "do not attribute intent, belief, or state-of-mind to the model" in section_text

    def test_data_dictionary_provider_quote_advisory_present(self) -> None:
        """CDA SME §5.5 provider-quote advisory is in DATA_DICTIONARY.md §12.

        Required per verdict: '**Note on quotation.**' with advice about
        attributing quotes to model output, not model intent.
        """
        text = DATA_DICTIONARY_PATH.read_text(encoding="utf-8")
        section_start = text.find("## 12. Published failures JSON shape")
        assert section_start != -1, "DATA_DICTIONARY.md §12 section not found."
        section_text = text[section_start:]
        assert "Note on quotation" in section_text, (
            "DATA_DICTIONARY.md §12 is missing the §5.5 provider-quote advisory "
            "('Note on quotation.')."
        )
        assert "attribute quotes to the model output, not to model intent" in section_text, (
            "DATA_DICTIONARY.md §12 is missing the §5.5 key advisory sentence about "
            "attributing to model output, not model intent."
        )

    def test_data_dictionary_forbidden_vocabulary_absent_in_section_12(self) -> None:
        """DATA_DICTIONARY.md §12 contains no forbidden vocabulary per CLAUDE.md §7.

        Checks LSB-authored prose in §12 for 'worldview', 'believes', 'refuses'
        (as a psychological attribution), and 'model refused' (direct intent claim).
        Verbatim model-output examples in doc are an exception (they are data).
        """
        text = DATA_DICTIONARY_PATH.read_text(encoding="utf-8")
        section_start = text.find("## 12. Published failures JSON shape")
        assert section_start != -1, "DATA_DICTIONARY.md §12 section not found."
        # Find the end of §12 (next ## header, or EOF).
        next_section = text.find("\n## ", section_start + 1)
        section_text = (
            text[section_start:next_section] if next_section != -1 else text[section_start:]
        )

        # Check that forbidden framing is absent from LSB-authored prose.
        # The §5.5 advisory intentionally uses "the model refused" as a BAD example
        # inside a quote — that is allowed. But standalone attribution is not.
        # We check for 'worldview' and 'believes' which have no legitimate use here.
        assert "worldview" not in section_text, (
            "DATA_DICTIONARY.md §12 contains forbidden vocabulary 'worldview'."
        )
        assert " believes" not in section_text, (
            "DATA_DICTIONARY.md §12 contains forbidden vocabulary 'believes'."
        )


# ---------------------------------------------------------------------------
# 6. API-key leak regression on published JSON output
# ---------------------------------------------------------------------------


class TestPublishedJsonNoSecrets:
    """Load the emitted JSON files and assert zero matches for secret patterns.

    This is the durable safeguard against future regressions in sanitization.
    It checks the actual output bytes, not the sanitization function in isolation.
    """

    # Patterns that must NOT appear in any published JSON file.
    _FORBIDDEN_PATTERNS = [
        re.compile(r"sk-ant-api[0-9]+-[a-zA-Z0-9_-]{10,}"),
        re.compile(r"sk-or-v1-[a-zA-Z0-9]{10,}"),
        re.compile(r"hf_[a-zA-Z0-9]{10,}"),
        re.compile(r"xoxb-[0-9A-Za-z-]{10,}"),
        re.compile(r"/opt/lsb-agent/"),
        re.compile(r"/home/lsb/"),
        re.compile(r"/home/markd/"),
    ]
    # Note: `data/raw/` is checked separately because it appears in doc strings
    # but NOT in published JSON string fields.

    def test_no_secrets_in_published_json(self, tmp_path: Path) -> None:
        """Published JSON output contains no secret-shaped strings."""
        from cdb_publish.failures import build_failures

        failures_path, di_path, inf_path = _copy_fixtures(tmp_path)
        out = tmp_path / "out"

        build_failures(
            raw_failures_path=failures_path,
            raw_decline_interviews_path=di_path,
            raw_informants_path=inf_path,
            output_dir=out,
            domain_slugs=["family", "holidays"],
        )

        for slug in ("family", "holidays"):
            output_text = (out / f"{slug}.json").read_text(encoding="utf-8")
            # Parse JSON and re-serialize to ensure we check the actual string
            # values, not JSON-escaped representations.
            parsed = json.loads(output_text)
            all_strings = _collect_strings(parsed)
            for pattern in self._FORBIDDEN_PATTERNS:
                matches = [s for s in all_strings if pattern.search(s)]
                assert not matches, (
                    f"Secret pattern '{pattern.pattern}' matched in {slug}.json "
                    f"string values: {matches[:3]}"
                )

    def test_no_data_raw_paths_in_published_records(self, tmp_path: Path) -> None:
        """Published JSON record strings do not contain data/raw/ paths."""
        from cdb_publish.failures import build_failures

        failures_path, di_path, inf_path = _copy_fixtures(tmp_path)
        out = tmp_path / "out"

        build_failures(
            raw_failures_path=failures_path,
            raw_decline_interviews_path=di_path,
            raw_informants_path=inf_path,
            output_dir=out,
            domain_slugs=["family"],
        )

        family = json.loads((out / "family.json").read_text(encoding="utf-8"))
        all_strings = _collect_strings(family["records"])
        # The pattern data/raw/ as a path prefix in string values is forbidden.
        path_pattern = re.compile(r"\bdata/raw/[^\s\"']+")
        matches = [s for s in all_strings if path_pattern.search(s)]
        assert not matches, (
            f"data/raw/ path pattern found in published record string values: {matches[:3]}"
        )


def _collect_strings(obj: object) -> list[str]:
    """Recursively collect all str values from a nested dict/list structure."""
    results: list[str] = []
    if isinstance(obj, str):
        results.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            results.extend(_collect_strings(v))
    elif isinstance(obj, list):
        for item in obj:
            results.extend(_collect_strings(item))
    return results


# ---------------------------------------------------------------------------
# 7. originating_outcome_class all 7 enum values surface verbatim
# ---------------------------------------------------------------------------


class TestOriginatingOutcomeClassAllValues:
    """Assert all 7 originating_outcome_class enum values are recognised as
    valid published values and that none are rewritten or filtered.

    The plan §2.4 and CDA SME §3 require verbatim surfacing of the enum.
    This test builds a minimal in-memory fixture for each value and checks
    round-trip fidelity.
    """

    ALL_SEVEN_VALUES = [
        "empty_output",
        "refusal_string_match",
        "single_degenerate_pile",
        "parse_failure",
        "http_error",
        "timeout",
        "other",
    ]

    def _make_di_jsonl(self, outcome_class: str, inf_id: str, di_id: str) -> str:
        """Return a JSONL line for a DeclineInterview with given outcome_class."""
        return json.dumps({
            "decline_interview_id": di_id,
            "originating_informant_id": inf_id,
            "originating_failure_id": None,
            "originating_step": "pile_sort",
            "originating_outcome_class": outcome_class,
            "detection_rule_version": "v1",
            "detection_timestamp": "2026-05-01T10:00:00Z",
            "followup_timestamp": "2026-05-01T10:05:00Z",
            "model_id": "test-model-x",
            "model_version_returned": "test-model-x-v1",
            "provider": "test",
            "api_endpoint": "https://test.example.com/v1/chat",
            "prompt_version": "decline_v1",
            "sha256_manifest": "a" * 64,
            "prompt_verbatim": "Describe what happened.",
            "response_verbatim": f"Test response for {outcome_class}.",
            "thinking_verbatim": "",
            "input_tokens": 50,
            "output_tokens": 20,
            "latency_ms": 500,
            "stop_reason": "stop",
            "qa_notes": "",
            "version_drift_flag": False,
        })

    def test_all_seven_outcome_classes_surface_verbatim(self, tmp_path: Path) -> None:
        """All 7 originating_outcome_class values survive round-trip to published JSON."""
        from cdb_publish.failures import build_failures

        # Build one decline_interview per outcome class with matching informant.
        informants_lines = []
        di_lines = []
        for i, oc in enumerate(self.ALL_SEVEN_VALUES):
            inf_id = f"inf-oc-{i:02d}"
            di_id = f"di-oc-{i:02d}-" + "a" * 16
            informants_lines.append(json.dumps({
                "informant_id": inf_id,
                "domain_slug": "family",
                "run_index": i,
                "collection_date": "2026-05-01T10:00:00Z",
                "model_id": "test-model-x",
                "model_version_returned": "test-model-x-v1",
                "family": "test",
                "provider": "test",
                "provider_request_id": f"req-oc-{i:02d}",
                "knowledge_cutoff": "2025-01-01",
                "open_weights": False,
                "origin_country": "us",
                "alignment_method": "rlhf",
                "collection_method": "api",
                "collection_mode": "live",
            }))
            di_lines.append(self._make_di_jsonl(oc, inf_id, di_id))

        failures_path = tmp_path / "failures.jsonl"
        di_path = tmp_path / "decline_interviews.jsonl"
        inf_path = tmp_path / "informants.jsonl"
        out = tmp_path / "out"

        failures_path.write_text("", encoding="utf-8")  # no failures needed
        di_path.write_text("\n".join(di_lines) + "\n", encoding="utf-8")
        inf_path.write_text("\n".join(informants_lines) + "\n", encoding="utf-8")

        build_failures(
            raw_failures_path=failures_path,
            raw_decline_interviews_path=di_path,
            raw_informants_path=inf_path,
            output_dir=out,
            domain_slugs=["family"],
        )

        family_json = json.loads((out / "family.json").read_text(encoding="utf-8"))
        published_oc_values = {
            r["originating_outcome_class"]
            for r in family_json["records"]
            if r["record_type"] == "decline_interview"
        }

        for expected_oc in self.ALL_SEVEN_VALUES:
            assert expected_oc in published_oc_values, (
                f"originating_outcome_class value '{expected_oc}' was not found "
                f"in published records. Got: {sorted(published_oc_values)}"
            )


# ---------------------------------------------------------------------------
# 8. cost_usd intentionally absent from published records
# ---------------------------------------------------------------------------


class TestCostUsdAbsent:
    """Assert cost_usd is not present in any published record (plan §5, CLAUDE.md R14)."""

    def test_cost_usd_not_in_published_records(self, tmp_path: Path) -> None:
        """cost_usd must not appear as a key in any published record."""
        from cdb_publish.failures import build_failures

        failures_path, di_path, inf_path = _copy_fixtures(tmp_path)
        out = tmp_path / "out"

        build_failures(
            raw_failures_path=failures_path,
            raw_decline_interviews_path=di_path,
            raw_informants_path=inf_path,
            output_dir=out,
            domain_slugs=["family", "holidays"],
        )

        for slug in ("family", "holidays"):
            data = json.loads((out / f"{slug}.json").read_text(encoding="utf-8"))
            for record in data["records"]:
                assert "cost_usd" not in record, (
                    f"cost_usd found in published {slug}.json record "
                    f"(record_type={record.get('record_type')}). "
                    "cost_usd is intentionally excluded per plan §5 and CLAUDE.md R14."
                )

    def test_cost_usd_not_in_top_level_published_file(self, tmp_path: Path) -> None:
        """cost_usd must not appear at the top level of any published failures JSON."""
        from cdb_publish.failures import build_failures

        failures_path, di_path, inf_path = _copy_fixtures(tmp_path)
        out = tmp_path / "out"

        build_failures(
            raw_failures_path=failures_path,
            raw_decline_interviews_path=di_path,
            raw_informants_path=inf_path,
            output_dir=out,
            domain_slugs=["family"],
        )

        data = json.loads((out / "family.json").read_text(encoding="utf-8"))
        assert "cost_usd" not in data


# ---------------------------------------------------------------------------
# 9. Manifest Pydantic schema failures field round-trips
# ---------------------------------------------------------------------------


class TestManifestSchemaFailuresField:
    """Assert the Manifest Pydantic schema has the failures field and it round-trips."""

    def test_manifest_has_failures_field(self) -> None:
        """Manifest schema carries failures: dict[str, str] per plan §2.7."""
        from cdb_publish.schemas.manifest import Manifest

        assert hasattr(Manifest.model_fields, "failures") or "failures" in Manifest.model_fields, (
            "Manifest schema is missing the 'failures' field added in T9 (plan §2.7)."
        )

    def test_manifest_failures_field_default_is_empty_dict(self) -> None:
        """Manifest failures field has default {} for backward compatibility."""
        from datetime import UTC, datetime

        from cdb_publish.schemas.manifest import Manifest

        m = Manifest(
            built_at=datetime(2026, 5, 12, 18, 0, 0, tzinfo=UTC),
            domains=[],
            oci_low_concentration_threshold=0.5,
        )
        assert m.failures == {}, (
            "Manifest.failures default is not {} — backward-compat broken."
        )

    def test_manifest_failures_field_round_trips(self) -> None:
        """Manifest.failures dict round-trips through Pydantic serialization."""
        from datetime import UTC, datetime

        from cdb_publish.schemas.manifest import Manifest

        failures_map = {
            "family": "data/failures/family.json",
            "holidays": "data/failures/holidays.json",
        }
        m = Manifest(
            built_at=datetime(2026, 5, 12, 18, 0, 0, tzinfo=UTC),
            domains=[],
            oci_low_concentration_threshold=0.5,
            failures=failures_map,
        )
        serialized = m.model_dump()
        assert serialized["failures"] == failures_map

    def test_manifest_failures_field_name_matches_data_dictionary(self) -> None:
        """The field name 'failures' in the Manifest schema matches DATA_DICTIONARY.md §12.6.

        String comparison test — catches field rename drift between schema and docs.
        """
        from cdb_publish.schemas.manifest import Manifest

        assert "failures" in Manifest.model_fields, (
            "Manifest schema does not have a field named 'failures'. "
            "DATA_DICTIONARY.md §12 documents this field; a rename would break "
            "the open data contract."
        )
        dd_text = DATA_DICTIONARY_PATH.read_text(encoding="utf-8")
        assert '"failures"' in dd_text or "`failures`" in dd_text, (
            "DATA_DICTIONARY.md does not mention the Manifest 'failures' field. "
            "Schema and dictionary have drifted."
        )


# ---------------------------------------------------------------------------
# 10. PublishedFailuresFile Pydantic validation of actual output
# ---------------------------------------------------------------------------


class TestPublishedFailuresFilePydanticValidation:
    """Validate actual build_failures() output against the PublishedFailuresFile
    Pydantic schema (acceptance criterion 3 from the plan).

    The Coder's tests check JSON shape field-by-field; this test runs the
    Pydantic validator over the entire emitted structure.
    """

    def test_family_output_validates_as_published_failures_file(
        self, tmp_path: Path
    ) -> None:
        """family.json output validates against PublishedFailuresFile schema."""
        from cdb_publish.failures import build_failures
        from cdb_publish.schemas.failures import PublishedFailuresFile

        failures_path, di_path, inf_path = _copy_fixtures(tmp_path)
        out = tmp_path / "out"

        build_failures(
            raw_failures_path=failures_path,
            raw_decline_interviews_path=di_path,
            raw_informants_path=inf_path,
            output_dir=out,
            domain_slugs=["family"],
        )

        raw = json.loads((out / "family.json").read_text(encoding="utf-8"))
        # Should not raise.
        validated = PublishedFailuresFile.model_validate(raw)
        assert validated.domain_slug == "family"
        assert validated.framing_note != ""
        assert isinstance(validated.records, list)

    def test_empty_domain_output_validates_as_published_failures_file(
        self, tmp_path: Path
    ) -> None:
        """Empty-domain output (records: []) validates against PublishedFailuresFile schema."""
        from cdb_publish.failures import build_failures
        from cdb_publish.schemas.failures import PublishedFailuresFile

        failures_path, di_path, inf_path = _copy_fixtures(tmp_path)
        out = tmp_path / "out"

        build_failures(
            raw_failures_path=failures_path,
            raw_decline_interviews_path=di_path,
            raw_informants_path=inf_path,
            output_dir=out,
            domain_slugs=["empty_domain"],
        )

        raw = json.loads((out / "empty_domain.json").read_text(encoding="utf-8"))
        validated = PublishedFailuresFile.model_validate(raw)
        assert validated.n_records == 0
        assert validated.records == []

    def test_both_record_types_validate(self, tmp_path: Path) -> None:
        """Published file with both failure and decline_interview records validates."""
        from cdb_publish.failures import build_failures
        from cdb_publish.schemas.failures import PublishedFailuresFile

        failures_path, di_path, inf_path = _copy_fixtures(tmp_path)
        out = tmp_path / "out"

        build_failures(
            raw_failures_path=failures_path,
            raw_decline_interviews_path=di_path,
            raw_informants_path=inf_path,
            output_dir=out,
            domain_slugs=["family"],
        )

        raw = json.loads((out / "family.json").read_text(encoding="utf-8"))
        validated = PublishedFailuresFile.model_validate(raw)

        record_types = {r.record_type for r in validated.records}
        assert "failure" in record_types, (
            "No 'failure' records in validated family.json output."
        )
        assert "decline_interview" in record_types, (
            "No 'decline_interview' records in validated family.json output."
        )
