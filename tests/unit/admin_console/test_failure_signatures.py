"""Unit tests for failure_signatures.py (T6).

Verifies: exactly five entries in FAILURE_SIGNATURES; log-source and
record-source checks are distinct; scan() detects all five signatures
from fixtures.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from cdb_social.admin_console.failure_signatures import (
    FAILURE_SIGNATURES,
    scan,
)

FIXTURES = Path(__file__).parent.parent.parent / "fixtures" / "ops_console"


# ---------------------------------------------------------------------------
# Table invariants
# ---------------------------------------------------------------------------


class TestTableInvariants:
    def test_exactly_five_entries(self) -> None:
        assert len(FAILURE_SIGNATURES) == 5

    def test_ids_are_unique(self) -> None:
        ids = [s.id for s in FAILURE_SIGNATURES]
        assert len(ids) == len(set(ids))

    def test_expected_ids_present(self) -> None:
        ids = {s.id for s in FAILURE_SIGNATURES}
        assert "auth_401" in ids
        assert "billing_credit_balance" in ids
        assert "model_404" in ids
        assert "parse_after_retries" in ids
        assert "refusal_streak" in ids

    def test_source_values_are_log_or_record(self) -> None:
        for sig in FAILURE_SIGNATURES:
            assert sig.source in ("log", "record"), (
                f"Signature {sig.id!r} has invalid source {sig.source!r}"
            )

    def test_log_source_entries_all_have_descriptions(self) -> None:
        for sig in FAILURE_SIGNATURES:
            if sig.source == "log":
                assert sig.description.strip(), f"{sig.id} has empty description"

    def test_no_vocabulary_shared_between_log_and_record_sources(self) -> None:
        """Pitfall-13 guard: log-source and record-source entries must not share
        vocabulary that could cause cross-boundary miscalibration.

        We check that the description for log-source entries does not mention
        'stop_reason', 'refusal', 'decline', 'content_filter', or 'safety_filter'
        (record-source vocabulary), and that the record-source description does not
        mention HTTP status codes or exception class names (log-source vocabulary).
        """
        log_vocab = {"stop_reason", "refusal", "decline", "content_filter", "safety_filter"}
        record_vocab = {"401", "402", "404", "PileSortParseError", "AuthenticationError"}

        for sig in FAILURE_SIGNATURES:
            if sig.source == "log":
                desc_lower = sig.description.lower()
                for term in log_vocab:
                    assert term not in desc_lower, (
                        f"Log-source signature {sig.id!r} description contains "
                        f"record-source term {term!r} (pitfall-13 violation)"
                    )
            elif sig.source == "record":
                for term in record_vocab:
                    assert term not in sig.description, (
                        f"Record-source signature {sig.id!r} description contains "
                        f"log-source term {term!r} (pitfall-13 violation)"
                    )

    def test_refusal_streak_is_record_source(self) -> None:
        sig = next(s for s in FAILURE_SIGNATURES if s.id == "refusal_streak")
        assert sig.source == "record"

    def test_log_source_count(self) -> None:
        log_sources = [s for s in FAILURE_SIGNATURES if s.source == "log"]
        assert len(log_sources) == 4

    def test_record_source_count(self) -> None:
        record_sources = [s for s in FAILURE_SIGNATURES if s.source == "record"]
        assert len(record_sources) == 1


# ---------------------------------------------------------------------------
# scan() with log fixtures
# ---------------------------------------------------------------------------


class TestScanLogSources:
    def test_detects_auth_401(self) -> None:
        log = FIXTURES / "log_auth_401.txt"
        hits = scan(log, {})
        ids = {h.signature_id for h in hits}
        assert "auth_401" in ids

    def test_detects_billing(self) -> None:
        log = FIXTURES / "log_billing.txt"
        hits = scan(log, {})
        ids = {h.signature_id for h in hits}
        assert "billing_credit_balance" in ids

    def test_detects_model_404(self) -> None:
        log = FIXTURES / "log_model_404.txt"
        hits = scan(log, {})
        ids = {h.signature_id for h in hits}
        assert "model_404" in ids

    def test_detects_parse_after_retries(self) -> None:
        log = FIXTURES / "log_parse_error.txt"
        hits = scan(log, {})
        ids = {h.signature_id for h in hits}
        assert "parse_after_retries" in ids

    def test_clean_log_produces_no_log_hits(self) -> None:
        log = FIXTURES / "log_clean.txt"
        hits = scan(log, {})
        log_hits = [h for h in hits if h.source == "log"]
        assert log_hits == []

    def test_absent_log_path_skips_log_checks(self, tmp_path: Path) -> None:
        missing = tmp_path / "missing.log"
        hits = scan(missing, {})
        log_hits = [h for h in hits if h.source == "log"]
        assert log_hits == []

    def test_none_log_path_skips_log_checks(self) -> None:
        hits = scan(None, {})
        log_hits = [h for h in hits if h.source == "log"]
        assert log_hits == []

    def test_hit_source_field_is_log(self) -> None:
        log = FIXTURES / "log_auth_401.txt"
        hits = scan(log, {})
        auth_hits = [h for h in hits if h.signature_id == "auth_401"]
        assert all(h.source == "log" for h in auth_hits)

    def test_hit_evidence_is_nonempty_string(self) -> None:
        log = FIXTURES / "log_auth_401.txt"
        hits = scan(log, {})
        for h in hits:
            assert isinstance(h.evidence, str)
            assert h.evidence.strip()

    def test_one_hit_per_signature_per_scan(self) -> None:
        # Log with two auth_401 lines; scan should return at most one hit
        # per signature (break after first match).
        log_text = "401 Unauthorized\nAnother 401 Unauthorized line\n"
        import tempfile
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".log", delete=False
        ) as f:
            f.write(log_text)
            log_path = Path(f.name)
        try:
            hits = scan(log_path, {})
            auth_hits = [h for h in hits if h.signature_id == "auth_401"]
            assert len(auth_hits) == 1
        finally:
            log_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# scan() with record-source (refusal_streak)
# ---------------------------------------------------------------------------


def _make_rec(stop_reason: str) -> dict[str, Any]:
    return {"freelist": {"stop_reason": stop_reason}}


class TestScanRecordSource:
    def test_no_refusal_streak_below_threshold(self, tmp_path: Path) -> None:
        records = {
            ("m", "d"): [_make_rec("refusal"), _make_rec("refusal")]
        }
        hits = scan(None, records)
        refusal_hits = [h for h in hits if h.signature_id == "refusal_streak"]
        assert refusal_hits == []

    def test_refusal_streak_at_threshold(self, tmp_path: Path) -> None:
        records = {
            ("m", "d"): [
                _make_rec("refusal"),
                _make_rec("refusal"),
                _make_rec("refusal"),
            ]
        }
        hits = scan(None, records)
        ids = {h.signature_id for h in hits}
        assert "refusal_streak" in ids

    def test_refusal_streak_above_threshold(self, tmp_path: Path) -> None:
        records = {
            ("m", "d"): [_make_rec("refusal")] * 5
        }
        hits = scan(None, records)
        ids = {h.signature_id for h in hits}
        assert "refusal_streak" in ids

    def test_refusal_streak_reset_by_normal_record(self, tmp_path: Path) -> None:
        records = {
            ("m", "d"): [
                _make_rec("refusal"),
                _make_rec("refusal"),
                _make_rec("end_turn"),  # resets streak
                _make_rec("refusal"),
                _make_rec("refusal"),
            ]
        }
        hits = scan(None, records)
        refusal_hits = [h for h in hits if h.signature_id == "refusal_streak"]
        assert refusal_hits == []

    def test_all_stop_reason_variants_count_as_refusal(self) -> None:
        for reason in ("refusal", "decline", "content_filter", "safety_filter"):
            records = {("m", "d"): [_make_rec(reason)] * 3}
            hits = scan(None, records)
            ids = {h.signature_id for h in hits}
            assert "refusal_streak" in ids, f"stop_reason={reason!r} not detected"

    def test_hit_source_field_is_record(self) -> None:
        records = {("m", "d"): [_make_rec("refusal")] * 3}
        hits = scan(None, records)
        streak_hits = [h for h in hits if h.signature_id == "refusal_streak"]
        assert all(h.source == "record" for h in streak_hits)

    def test_streak_detected_in_real_fixture(self) -> None:
        """z-ai/glm-5.2 has three consecutive refusal records in the fixture."""
        import json

        jsonl_path = FIXTURES / "informants_mixed.jsonl"
        records_by_model_domain: dict[tuple[str, str], list[dict[str, Any]]] = {}
        for line in jsonl_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            key = (rec.get("model_id", ""), rec.get("domain_slug", ""))
            records_by_model_domain.setdefault(key, []).append(rec)

        hits = scan(None, records_by_model_domain)
        ids = {h.signature_id for h in hits}
        assert "refusal_streak" in ids

    def test_no_cross_model_domain_contamination(self) -> None:
        """Streak in one (model, domain) must not trigger a hit for another."""
        records = {
            ("m1", "d"): [_make_rec("refusal")] * 3,
            ("m2", "d"): [_make_rec("end_turn")] * 5,
        }
        hits = scan(None, records)
        streak_hits = [h for h in hits if h.signature_id == "refusal_streak"]
        # Only m1 / d should trigger
        assert all("m1" in h.evidence for h in streak_hits)
