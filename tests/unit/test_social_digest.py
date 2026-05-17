"""Unit tests for cdb_social/digest.py — Phase 7 T6a.

Test classes:
  TestFormatTriggerSummary   — one test per TriggerType, binding wording verified
  TestForbiddenWordingAbsent — digest body never contains forbidden phrases
  TestFormatDigest           — full digest body structure test
  TestFormatDigestEmpty      — empty trigger list raises ValueError
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from cdb_core.schemas import SocialTrigger, TriggerType
from cdb_social.digest import format_digest, format_trigger_summary

# ─────────────────────────────────────────────────────────────────────────────
# Fixture helpers
# ─────────────────────────────────────────────────────────────────────────────

_DETECT_AT = datetime(2026, 5, 17, 14, 0, 0, tzinfo=UTC)


def _make_new_model_trigger() -> SocialTrigger:
    return SocialTrigger(
        trigger_type=TriggerType.NEW_MODEL,
        detected_at=_DETECT_AT,
        domain_slug="family",
        model_id="claude-opus-4-8",
        evidence={"first_seen_in_domain": "family"},
        dedupe_key="abcd1234abcd1234",
    )


def _make_new_domain_trigger() -> SocialTrigger:
    return SocialTrigger(
        trigger_type=TriggerType.NEW_DOMAIN,
        detected_at=_DETECT_AT,
        domain_slug="emotion",
        model_id=None,
        evidence={"domain_slug": "emotion", "n_models": 8},
        dedupe_key="bbbb2222bbbb2222",
    )


def _make_divergence_trigger() -> SocialTrigger:
    return SocialTrigger(
        trigger_type=TriggerType.DIVERGENCE,
        detected_at=_DETECT_AT,
        domain_slug="family",
        model_id=None,
        evidence={
            "domain_slug": "family",
            "model_pair": ["claude-opus-4-7", "gemini-2.5-pro"],
            "old_high": 0.42,
            "new_high": 0.51,
            "gap_delta": 0.09,
        },
        dedupe_key="cccc3333cccc3333",
    )


def _make_drift_trigger() -> SocialTrigger:
    return SocialTrigger(
        trigger_type=TriggerType.DRIFT,
        detected_at=_DETECT_AT,
        domain_slug=None,
        model_id=None,
        evidence={
            "model_version_returned": "claude-opus-4-7",
            "procrustes_distance": 0.17,
            "date_pair": ["2026-04-10", "2026-05-15"],
        },
        dedupe_key="dddd4444dddd4444",
    )


def _make_monthly_roundup_trigger() -> SocialTrigger:
    return SocialTrigger(
        trigger_type=TriggerType.MONTHLY_ROUNDUP,
        detected_at=_DETECT_AT,
        domain_slug=None,
        model_id=None,
        evidence={"month": "2026-04"},
        dedupe_key="eeee5555eeee5555",
    )


def _all_triggers() -> list[SocialTrigger]:
    return [
        _make_new_model_trigger(),
        _make_new_domain_trigger(),
        _make_divergence_trigger(),
        _make_drift_trigger(),
        _make_monthly_roundup_trigger(),
    ]


# ─────────────────────────────────────────────────────────────────────────────
# TestFormatTriggerSummary
# ─────────────────────────────────────────────────────────────────────────────


class TestFormatTriggerSummary:
    """One test per TriggerType verifying binding wording per T5 CDA SME §5.5/§5.7."""

    def test_new_model_summary(self) -> None:
        trigger = _make_new_model_trigger()
        result = format_trigger_summary(trigger)
        assert "claude-opus-4-8" in result
        assert "family" in result
        assert "added to" in result

    def test_new_domain_summary(self) -> None:
        trigger = _make_new_domain_trigger()
        result = format_trigger_summary(trigger)
        assert "emotion" in result
        assert "domain added" in result
        assert "n=8" in result

    def test_divergence_uses_max_pairwise_distance(self) -> None:
        """Binding wording: "max pairwise distance" not "pairwise gap"."""
        trigger = _make_divergence_trigger()
        result = format_trigger_summary(trigger)
        assert "max pairwise distance" in result, (
            f"Expected 'max pairwise distance' in DIVERGENCE summary, got: {result!r}"
        )
        assert "pairwise gap" not in result, (
            f"Forbidden phrasing 'pairwise gap' found in DIVERGENCE summary: {result!r}"
        )

    def test_divergence_contains_model_pair(self) -> None:
        trigger = _make_divergence_trigger()
        result = format_trigger_summary(trigger)
        assert "claude-opus-4-7" in result
        assert "gemini-2.5-pro" in result

    def test_divergence_contains_distance_values(self) -> None:
        trigger = _make_divergence_trigger()
        result = format_trigger_summary(trigger)
        # Values formatted to 2 decimal places
        assert "0.42" in result
        assert "0.51" in result
        assert "0.09" in result

    def test_drift_uses_procrustes_distance(self) -> None:
        """Binding wording: "Procrustes distance" verbatim (Register-3)."""
        trigger = _make_drift_trigger()
        result = format_trigger_summary(trigger)
        assert "Procrustes distance" in result, (
            f"Expected 'Procrustes distance' in DRIFT summary, got: {result!r}"
        )

    def test_drift_contains_placeholder_caveat(self) -> None:
        """Binding: placeholder caveat is mandatory while §7.3 lockout is engaged."""
        trigger = _make_drift_trigger()
        result = format_trigger_summary(trigger)
        assert "threshold 0.15 placeholder" in result, (
            f"Expected 'threshold 0.15 placeholder' caveat in DRIFT summary, "
            f"got: {result!r}"
        )
        assert "lockout engaged" in result, (
            f"Expected 'lockout engaged' in DRIFT summary, got: {result!r}"
        )

    def test_drift_contains_model_and_dates(self) -> None:
        trigger = _make_drift_trigger()
        result = format_trigger_summary(trigger)
        assert "claude-opus-4-7" in result
        assert "2026-04-10" in result
        assert "2026-05-15" in result

    def test_monthly_roundup_uses_binding_phrasing(self) -> None:
        """Binding wording: "Monthly cross-domain categorical-structure roundup".

        This applies the T1 §5.7 amendment at the email layer — the pre-amendment
        "state of cultural alignment roundup" phrasing must NOT appear.
        """
        trigger = _make_monthly_roundup_trigger()
        result = format_trigger_summary(trigger)
        assert "Monthly cross-domain categorical-structure roundup" in result, (
            f"Expected binding MONTHLY_ROUNDUP phrasing, got: {result!r}"
        )

    def test_monthly_roundup_contains_month(self) -> None:
        trigger = _make_monthly_roundup_trigger()
        result = format_trigger_summary(trigger)
        assert "2026-04" in result

    def test_monthly_roundup_forbidden_phrasing_absent(self) -> None:
        """The pre-amendment phrasing must not appear anywhere in the summary."""
        trigger = _make_monthly_roundup_trigger()
        result = format_trigger_summary(trigger)
        assert "state of cultural alignment" not in result, (
            f"Forbidden pre-amendment phrasing found in MONTHLY_ROUNDUP summary: {result!r}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# TestForbiddenWordingAbsent
# ─────────────────────────────────────────────────────────────────────────────


class TestForbiddenWordingAbsent:
    """Assert the digest body never contains §1.5.4 forbidden vocabulary."""

    def _make_digest_body(self) -> str:
        triggers = _all_triggers()
        queue_counts = {"pending": 2, "approved": 1, "published": 14, "failed": 3}
        _, body = format_digest(
            triggers,
            queue_counts=queue_counts,
            digest_date=datetime(2026, 5, 17, 14, 0, 0, tzinfo=UTC),
        )
        return body

    def test_no_pairwise_gap(self) -> None:
        """'pairwise gap' is the forbidden alternative to 'max pairwise distance'."""
        body = self._make_digest_body()
        assert "pairwise gap" not in body, (
            "Forbidden phrase 'pairwise gap' found in digest body"
        )

    def test_no_state_of_cultural_alignment(self) -> None:
        """Pre-amendment MONTHLY_ROUNDUP phrasing must not appear."""
        body = self._make_digest_body()
        assert "state of cultural alignment" not in body, (
            "Forbidden pre-amendment phrase found in digest body"
        )

    def test_no_worldview(self) -> None:
        """§1.5.4 left-column: 'worldview' applied to models."""
        body = self._make_digest_body()
        # "worldview" is forbidden in model-facing contexts
        assert "worldview" not in body.lower(), (
            "Forbidden vocabulary 'worldview' found in digest body"
        )

    def test_no_believes(self) -> None:
        """§1.5.4 left-column: 'believes' applied to models."""
        body = self._make_digest_body()
        assert "believes" not in body.lower(), (
            "Forbidden vocabulary 'believes' found in digest body"
        )

    def test_no_cultural_bias(self) -> None:
        """§1.5.4 left-column: 'cultural bias' (standalone)."""
        body = self._make_digest_body()
        assert "cultural bias" not in body.lower(), (
            "Forbidden phrase 'cultural bias' found in digest body"
        )

    def test_no_model_believes(self) -> None:
        """Explicit check: 'model X believes' phrasing."""
        body = self._make_digest_body()
        # The body should not say a model "believes" anything
        import re
        pattern = re.compile(r"model\s+\w+\s+believes", re.IGNORECASE)
        assert not pattern.search(body), (
            "Forbidden 'model X believes' phrasing found in digest body"
        )


# ─────────────────────────────────────────────────────────────────────────────
# TestFormatDigest
# ─────────────────────────────────────────────────────────────────────────────


class TestFormatDigest:
    """Full digest body structure — subject, header, numbered list, queue, instructions."""

    def _call(
        self,
        triggers: list[SocialTrigger] | None = None,
        queue_counts: dict[str, int] | None = None,
        digest_date: datetime | None = None,
    ) -> tuple[str, str]:
        return format_digest(
            triggers if triggers is not None else _all_triggers(),
            queue_counts=queue_counts or {
                "pending": 2, "approved": 1, "published": 14, "failed": 3
            },
            digest_date=digest_date or datetime(2026, 5, 17, 14, 0, 0, tzinfo=UTC),
        )

    def test_subject_format(self) -> None:
        subject, _ = self._call()
        assert subject == "LSB daily digest 2026-05-17"

    def test_body_header_present(self) -> None:
        _, body = self._call()
        assert "LSB daily digest 2026-05-17" in body

    def test_body_trigger_count_line(self) -> None:
        triggers = _all_triggers()
        _, body = self._call(triggers=triggers)
        assert f"{len(triggers)} trigger(s) detected since the last digest" in body

    def test_body_numbered_list(self) -> None:
        """Each trigger appears with a [N] prefix."""
        triggers = _all_triggers()
        _, body = self._call(triggers=triggers)
        for i in range(1, len(triggers) + 1):
            assert f"[{i}]" in body, f"Missing trigger index [{i}] in digest body"

    def test_body_queue_status_section(self) -> None:
        _, body = self._call()
        assert "Queue status:" in body
        assert "pending:" in body
        assert "approved:" in body
        assert "published:" in body
        assert "failed:" in body

    def test_body_pending_count(self) -> None:
        counts = {"pending": 5, "approved": 0, "published": 0, "failed": 0}
        _, body = self._call(queue_counts=counts)
        assert "5 draft(s) awaiting your review" in body

    def test_body_approved_count(self) -> None:
        counts = {"pending": 0, "approved": 3, "published": 0, "failed": 0}
        _, body = self._call(queue_counts=counts)
        assert "3 draft(s) awaiting publication" in body

    def test_body_instructions_present(self) -> None:
        """The body must include the admin console instruction."""
        _, body = self._call()
        assert "python -m cdb_social.admin_console" in body
        assert "127.0.0.1:8000" in body

    def test_body_divergence_binding_wording_present(self) -> None:
        """DIVERGENCE trigger in digest body uses 'max pairwise distance'."""
        triggers = [_make_divergence_trigger()]
        _, body = self._call(triggers=triggers)
        assert "max pairwise distance" in body

    def test_body_drift_binding_wording_present(self) -> None:
        """DRIFT trigger in digest body uses 'Procrustes distance'."""
        triggers = [_make_drift_trigger()]
        _, body = self._call(triggers=triggers)
        assert "Procrustes distance" in body

    def test_body_monthly_roundup_binding_wording_present(self) -> None:
        """MONTHLY_ROUNDUP trigger in digest body uses canonical phrasing."""
        triggers = [_make_monthly_roundup_trigger()]
        _, body = self._call(triggers=triggers)
        assert "Monthly cross-domain categorical-structure roundup" in body

    def test_single_trigger_digest(self) -> None:
        """A digest with a single trigger produces correct count and [1] prefix."""
        triggers = [_make_new_model_trigger()]
        subject, body = self._call(triggers=triggers)
        assert "1 trigger(s) detected" in body
        assert "[1]" in body
        assert "[2]" not in body

    def test_date_in_subject_matches_digest_date(self) -> None:
        subject, _ = self._call(
            digest_date=datetime(2026, 3, 15, 14, 0, 0, tzinfo=UTC)
        )
        assert subject == "LSB daily digest 2026-03-15"


# ─────────────────────────────────────────────────────────────────────────────
# TestFormatDigestEmpty
# ─────────────────────────────────────────────────────────────────────────────


class TestFormatDigestEmpty:
    """format_digest with zero triggers raises ValueError.

    The CLI is what enforces zero-send; format_digest itself raises on empty
    input so the contract is explicit rather than silently producing an empty body.
    """

    def test_empty_triggers_raises(self) -> None:
        with pytest.raises(ValueError, match="empty trigger list"):
            format_digest(
                [],
                queue_counts={"pending": 0, "approved": 0, "published": 0, "failed": 0},
                digest_date=datetime(2026, 5, 17, 14, 0, 0, tzinfo=UTC),
            )
