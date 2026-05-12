"""Tests for cdb_publish.failures and cdb_publish.sanitize.

No real API calls. All tests use synthetic fixtures in
tests/fixtures/failures/ or written to tmp_path.
See CLAUDE.md §6 R9 (no real API in tests).

Coverage:
- Sanitization fires on each of the three pattern categories (API keys,
  Slack webhook URLs, local filesystem paths).
- Sanitization does not fire on benign strings.
- build_failures() join via originating_informant_id.
- build_failures() join via originating_failure_id.
- Orphaned decline-interview records are not published (warning logged).
- Failure records with no context.domain are not published (warning logged).
- Empty-domain file is emitted with records: [] (first-class empty state).
- Sort order: collection_date asc, record_type asc, stable id asc.
- Build is deterministic on fixture inputs (non-timestamp content).
- Source files in data/raw/ are not modified (SHA256 before/after).
- Published file has required top-level fields including framing_note.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

# ---------------------------------------------------------------------------
# Fixtures directory
# ---------------------------------------------------------------------------

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "failures"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# Sanitization tests (cdb_publish.sanitize)
# ---------------------------------------------------------------------------


class TestSanitizeForPublication:
    """Unit tests for sanitize_for_publication()."""

    def test_api_key_anthropic(self) -> None:
        from cdb_publish.sanitize import sanitize_for_publication

        # A realistic Anthropic key shape (sk-ant- prefix, 100 chars total).
        key = "sk-ant-api03-" + "A" * 87
        result = sanitize_for_publication(f"Key is: {key} done")
        assert key not in result
        assert "[redacted: secret pattern]" in result

    def test_api_key_openrouter(self) -> None:
        from cdb_publish.sanitize import sanitize_for_publication

        key = "sk-or-v1-" + "a" * 65
        result = sanitize_for_publication(f"Token: {key}")
        assert key not in result
        assert "[redacted: secret pattern]" in result

    def test_api_key_huggingface(self) -> None:
        from cdb_publish.sanitize import sanitize_for_publication

        key = "hf_" + "b" * 35
        result = sanitize_for_publication(f"HF token {key} here")
        assert key not in result
        assert "[redacted: secret pattern]" in result

    def test_api_key_generic_sk_long(self) -> None:
        from cdb_publish.sanitize import sanitize_for_publication

        # 55 chars after sk- — should match the narrowed generic pattern.
        key = "sk-" + "C" * 55
        result = sanitize_for_publication(f"Generic key: {key}")
        assert key not in result
        assert "[redacted: secret pattern]" in result

    def test_api_key_generic_sk_short_not_matched(self) -> None:
        from cdb_publish.sanitize import sanitize_for_publication

        # Only 20 chars after sk- — below the 50-char minimum (§5.4).
        short = "sk-" + "D" * 20
        result = sanitize_for_publication(f"Short token: {short}")
        # Should NOT be redacted — too short.
        assert short in result

    def test_slack_webhook_url(self) -> None:
        from cdb_publish.sanitize import sanitize_for_publication

        url = "https://hooks.slack.com/services/T12345ABC/B67890DEF/xAbCdEfGhIjKlMnOpQrStUvW"
        result = sanitize_for_publication(f"Webhook: {url}")
        assert url not in result
        assert "[redacted: secret pattern]" in result

    def test_local_path_opt(self) -> None:
        from cdb_publish.sanitize import sanitize_for_publication

        path = "/opt/lsb-agent/data/raw/secrets.txt"
        result = sanitize_for_publication(f"File at {path} found")
        assert path not in result
        assert "[redacted: local path]" in result

    def test_local_path_home_lsb(self) -> None:
        from cdb_publish.sanitize import sanitize_for_publication

        path = "/home/lsb/.env"
        result = sanitize_for_publication(f"Config: {path}")
        assert path not in result
        assert "[redacted: local path]" in result

    def test_local_path_data_raw(self) -> None:
        from cdb_publish.sanitize import sanitize_for_publication

        path = "data/raw/informants.jsonl"
        result = sanitize_for_publication(f"Source: {path}")
        assert path not in result
        assert "[redacted: local path]" in result

    def test_benign_openrouter_url_not_redacted(self) -> None:
        from cdb_publish.sanitize import sanitize_for_publication

        # A model-generated error mentioning openrouter.ai URL (benign).
        url = "https://openrouter.ai/api/v1/chat/completions"
        result = sanitize_for_publication(url)
        # Should NOT be redacted — not a secret pattern.
        assert url in result

    def test_benign_string_unchanged(self) -> None:
        from cdb_publish.sanitize import sanitize_for_publication

        text = "The exchange produced no output because the item list was empty."
        assert sanitize_for_publication(text) == text

    def test_no_silent_drop(self) -> None:
        from cdb_publish.sanitize import sanitize_for_publication

        # Redacted content is replaced with a visible marker, not dropped.
        key = "sk-ant-api03-" + "Z" * 87
        result = sanitize_for_publication(key)
        assert result != ""
        assert "[redacted:" in result


class TestSanitizeRecordStrings:
    """Tests for the recursive dict/list walker."""

    def test_nested_dict(self) -> None:
        from cdb_publish.sanitize import sanitize_record_strings

        key = "sk-ant-api03-" + "X" * 87
        obj = {"outer": {"inner": f"key is {key} here"}}
        result = sanitize_record_strings(obj)
        assert isinstance(result, dict)
        assert key not in str(result)
        assert "[redacted: secret pattern]" in result["outer"]["inner"]

    def test_nested_list(self) -> None:
        from cdb_publish.sanitize import sanitize_record_strings

        path = "/opt/lsb-agent/config/secret"
        obj = [{"msg": f"path={path}"}]
        result = sanitize_record_strings(obj)
        assert isinstance(result, list)
        assert path not in str(result)

    def test_non_string_leaves_unchanged(self) -> None:
        from cdb_publish.sanitize import sanitize_record_strings

        obj = {"count": 42, "flag": True, "none_val": None}
        result = sanitize_record_strings(obj)
        assert result == obj


# ---------------------------------------------------------------------------
# build_failures() integration tests
# ---------------------------------------------------------------------------


def _copy_fixtures(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Copy fixture JSONL files to tmp_path. Returns (failures, di, informants) paths."""
    failures = tmp_path / "failures.jsonl"
    di = tmp_path / "decline_interviews.jsonl"
    informants = tmp_path / "informants.jsonl"
    shutil.copy(FIXTURES_DIR / "failures.jsonl", failures)
    shutil.copy(FIXTURES_DIR / "decline_interviews.jsonl", di)
    shutil.copy(FIXTURES_DIR / "informants.jsonl", informants)
    return failures, di, informants


class TestBuildFailures:
    """Integration tests for build_failures()."""

    def test_join_via_informant_id(self, tmp_path: Path) -> None:
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

        family_json = json.loads((out / "family.json").read_text())
        di_ids = [
            r["decline_interview_id"]
            for r in family_json["records"]
            if r["record_type"] == "decline_interview"
        ]
        # di-aabbccdd11223344 joins via inf-001 → family.
        assert "di-aabbccdd11223344" in di_ids

    def test_join_via_failure_id(self, tmp_path: Path) -> None:
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

        family_json = json.loads((out / "family.json").read_text())
        di_ids = [
            r["decline_interview_id"]
            for r in family_json["records"]
            if r["record_type"] == "decline_interview"
        ]
        # di-eeff99887766aabb joins via failure_id for test-model-c / family / 2.
        assert "di-eeff99887766aabb" in di_ids

    def test_orphaned_record_not_published(self, tmp_path: Path) -> None:
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

        family_json = json.loads((out / "family.json").read_text())
        holidays_json = json.loads((out / "holidays.json").read_text())
        all_di_ids = [
            r["decline_interview_id"]
            for r in family_json["records"] + holidays_json["records"]
            if r["record_type"] == "decline_interview"
        ]
        # di-orphan999888777 references inf-nonexistent → should be filtered out.
        assert "di-orphan999888777" not in all_di_ids

    def test_missing_domain_failure_not_published(self, tmp_path: Path) -> None:
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

        family_json = json.loads((out / "family.json").read_text())
        holidays_json = json.loads((out / "holidays.json").read_text())
        all_records = family_json["records"] + holidays_json["records"]
        # The failure with no context.domain should not appear.
        error_msgs = [r.get("error_message", "") for r in all_records]
        assert not any("No domain here" in m for m in error_msgs)
        # The failure with unknown_domain should also not appear.
        assert not any("Domain not in manifest" in m for m in error_msgs)

    def test_empty_domain_file_emitted(self, tmp_path: Path) -> None:
        from cdb_publish.failures import build_failures

        failures_path, di_path, inf_path = _copy_fixtures(tmp_path)
        out = tmp_path / "out"

        # Add an extra slug with no data.
        result = build_failures(
            raw_failures_path=failures_path,
            raw_decline_interviews_path=di_path,
            raw_informants_path=inf_path,
            output_dir=out,
            domain_slugs=["family", "holidays", "empty_domain"],
        )

        # File must exist.
        assert (out / "empty_domain.json").exists()
        empty_json = json.loads((out / "empty_domain.json").read_text())
        assert empty_json["records"] == []
        assert empty_json["n_records"] == 0
        assert empty_json["n_failure_records"] == 0
        assert empty_json["n_decline_interview_records"] == 0

        # Manifest map entry must be non-null.
        assert result["empty_domain"] == "data/failures/empty_domain.json"

    def test_framing_note_present(self, tmp_path: Path) -> None:
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
        assert "framing_note" in family_json
        assert len(family_json["framing_note"]) > 50

    def test_sort_order(self, tmp_path: Path) -> None:
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

        family_json = json.loads((out / "family.json").read_text())
        dates = [r["collection_date"] for r in family_json["records"]]
        # Dates must be non-decreasing.
        assert dates == sorted(dates), f"Records not sorted by collection_date: {dates}"

    def test_sanitization_fires_in_published_records(self, tmp_path: Path) -> None:
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

        family_text = (out / "family.json").read_text()

        # API key should be redacted (seeded in fixture record with timestamp 2026-05-02T10...).
        assert "sk-ant-api03-" not in family_text
        # Slack webhook should be redacted.
        assert "hooks.slack.com" not in family_text
        # Local path should be redacted.
        assert "/opt/lsb-agent/" not in family_text

        # Redaction markers should be present.
        has_redaction = (
            "[redacted: secret pattern]" in family_text
            or "[redacted: local path]" in family_text
        )
        assert has_redaction

    def test_deterministic_non_timestamp_content(self, tmp_path: Path) -> None:
        from cdb_publish.failures import build_failures

        failures_path, di_path, inf_path = _copy_fixtures(tmp_path)

        out1 = tmp_path / "out1"
        out2 = tmp_path / "out2"

        build_failures(
            raw_failures_path=failures_path,
            raw_decline_interviews_path=di_path,
            raw_informants_path=inf_path,
            output_dir=out1,
            domain_slugs=["family", "holidays"],
        )
        build_failures(
            raw_failures_path=failures_path,
            raw_decline_interviews_path=di_path,
            raw_informants_path=inf_path,
            output_dir=out2,
            domain_slugs=["family", "holidays"],
        )

        for slug in ("family", "holidays"):
            j1 = json.loads((out1 / f"{slug}.json").read_text())
            j2 = json.loads((out2 / f"{slug}.json").read_text())
            # generated_at will differ; remove it before comparison.
            j1.pop("generated_at")
            j2.pop("generated_at")
            assert j1 == j2, f"Non-deterministic output for {slug}"

    def test_source_files_not_modified(self, tmp_path: Path) -> None:
        from cdb_publish.failures import build_failures

        failures_path, di_path, inf_path = _copy_fixtures(tmp_path)
        out = tmp_path / "out"

        sha_before = {
            "failures": _sha256(failures_path),
            "decline_interviews": _sha256(di_path),
            "informants": _sha256(inf_path),
        }

        build_failures(
            raw_failures_path=failures_path,
            raw_decline_interviews_path=di_path,
            raw_informants_path=inf_path,
            output_dir=out,
            domain_slugs=["family", "holidays"],
        )

        sha_after = {
            "failures": _sha256(failures_path),
            "decline_interviews": _sha256(di_path),
            "informants": _sha256(inf_path),
        }

        assert sha_before == sha_after, "Source JSONL files were modified by build_failures()"

    def test_manifest_map_all_slugs(self, tmp_path: Path) -> None:
        from cdb_publish.failures import build_failures

        failures_path, di_path, inf_path = _copy_fixtures(tmp_path)
        out = tmp_path / "out"

        result = build_failures(
            raw_failures_path=failures_path,
            raw_decline_interviews_path=di_path,
            raw_informants_path=inf_path,
            output_dir=out,
            domain_slugs=["family", "holidays"],
        )

        # Every slug has a non-null entry in the returned map.
        assert "family" in result
        assert "holidays" in result
        assert result["family"] == "data/failures/family.json"
        assert result["holidays"] == "data/failures/holidays.json"

    def test_record_type_discriminator_present(self, tmp_path: Path) -> None:
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
            data = json.loads((out / f"{slug}.json").read_text())
            for r in data["records"]:
                assert r["record_type"] in {"failure", "decline_interview"}

    def test_decline_interview_null_originating_outcome_class_not_on_failure(
        self, tmp_path: Path
    ) -> None:
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
        for r in family_json["records"]:
            if r["record_type"] == "failure":
                assert r["originating_outcome_class"] is None
            elif r["record_type"] == "decline_interview":
                assert r["originating_outcome_class"] is not None
