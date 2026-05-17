"""Unit tests for scripts/social_review.py — Phase 7 T5.

Tests organised by test class per CDA SME T5 §5.x:
  TestTriggerSummaryStrings     — §5.7 five per-TriggerType canonical patterns
  TestDraftSelfRatingLabel      — §5.1 "Drafter self-rating" not "Confidence"
  TestFramingChecksDisplay      — §5.2 canonical keys verbatim; extra keys below
  TestRejectFlow                — §5.3 five-code enum; sidecar JSON; re-prompts on invalid
  TestEditFlowPasses            — §5.4/§5.5 editor pass → approved/; text_history appended
  TestEditFlowFails             — §5.5 validator-as-subject wording; draft → pending/
  TestApproveFlow               — y → approved/
  TestSkipFlow                  — s → advance; no state change
  TestQuitFlow                  — q → stop; remaining drafts in pending/
  TestMonthlyRoundupSummary     — §5.7/§5.11 correct binding wording
  TestDriftSummaryCaveat        — §5.7 mandatory placeholder caveat
  TestDivergenceSummaryWording  — §5.7 "max pairwise distance" NOT "pairwise gap"

All tests use monkeypatch for input() and subprocess.run. No real API calls.
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime, timedelta
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest
from cdb_core.schemas import Platform, SocialDraft, SocialTrigger, TriggerType
from cdb_social.queue import load_draft, save_draft

# Import the module under test.
# social_review.py lives in scripts/ which is not a Python package;
# we import it via importlib.
_SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(_SCRIPTS_DIR))
import social_review as _cli  # noqa: E402

# ─────────────────────────────────────────────────────────────────────────────
# Shared fixture helpers
# ─────────────────────────────────────────────────────────────────────────────


def _make_trigger(
    trigger_type: TriggerType = TriggerType.NEW_MODEL,
    domain_slug: str | None = "family",
    model_id: str | None = "test-model-1",
    evidence: dict | None = None,
    dedupe_key: str = "abcdef0123456789",
) -> SocialTrigger:
    return SocialTrigger(
        trigger_type=trigger_type,
        detected_at=datetime(2026, 5, 17, 12, 0, 0, tzinfo=UTC),
        domain_slug=domain_slug,
        model_id=model_id,
        evidence=evidence or {"first_seen_in_domain": "family"},
        dedupe_key=dedupe_key,
    )


def _make_draft(
    draft_id: str = "draft_test001",
    trigger: SocialTrigger | None = None,
    text: str = "Test post with corpus lens patterns.",
    framing_checks: dict | None = None,
    framing_check_passed: bool = True,
    created_at: datetime | None = None,
    drafter_self_rating: float = 0.5,
    text_history: list[str] | None = None,
) -> SocialDraft:
    _framing_checks = framing_checks or {
        "hypothesis_framing": True,
        "cognition_attribution": True,
        "bare_numeric_without_ci": True,
        "register_boundary": True,
    }
    return SocialDraft(
        draft_id=draft_id,
        trigger=trigger or _make_trigger(),
        platform=Platform.BLUESKY,
        text=text,
        text_history=text_history or [],
        suggested_posting_time=datetime(2026, 5, 17, 14, 0, 0, tzinfo=UTC),
        drafter_self_rating=drafter_self_rating,
        methodology_url="https://cogstructurelab.com/family",
        dashboard_url="https://cogstructurelab.com/family",
        forbidden_terms_hit=[],
        framing_check_passed=framing_check_passed,
        framing_checks=_framing_checks,
        drafter_version="v1",
        prompt_version="v1",
        created_at=created_at or datetime(2026, 5, 17, 10, 0, 0, tzinfo=UTC),
    )


@pytest.fixture()
def queue_root(tmp_path: Path) -> Path:
    root = tmp_path / "queue"
    for state in ("pending", "approved", "failed"):
        (root / state).mkdir(parents=True)
    (root / "published").mkdir(parents=True)
    return root


def _save_pending(draft: SocialDraft, queue_root: Path) -> Path:
    path = queue_root / "pending" / f"{draft.draft_id}.json"
    save_draft(draft, path)
    return path


# ─────────────────────────────────────────────────────────────────────────────
# TestTriggerSummaryStrings
# ─────────────────────────────────────────────────────────────────────────────


class TestTriggerSummaryStrings:
    """§5.7 — Five per-TriggerType canonical summary patterns."""

    def test_new_model_summary(self) -> None:
        trigger = _make_trigger(
            trigger_type=TriggerType.NEW_MODEL,
            domain_slug="family",
            model_id="gpt-5-turbo",
            evidence={"first_seen_in_domain": "family"},
        )
        summary = _cli.format_trigger_summary(trigger)
        assert "gpt-5-turbo" in summary
        assert "family" in summary
        assert "added to" in summary
        assert "first seen in domain" in summary

    def test_new_domain_summary(self) -> None:
        trigger = _make_trigger(
            trigger_type=TriggerType.NEW_DOMAIN,
            domain_slug="religion",
            model_id=None,
            evidence={"domain_slug": "religion", "n_models": 14},
        )
        summary = _cli.format_trigger_summary(trigger)
        assert "religion" in summary
        assert "domain added" in summary
        assert "n=14" in summary

    def test_divergence_summary(self) -> None:
        trigger = _make_trigger(
            trigger_type=TriggerType.DIVERGENCE,
            domain_slug="food",
            model_id=None,
            evidence={
                "domain_slug": "food",
                "model_pair": ["gpt-4o", "claude-opus-4-6"],
                "old_high": 0.42,
                "new_high": 0.67,
                "gap_delta": 0.25,
            },
        )
        summary = _cli.format_trigger_summary(trigger)
        assert "food" in summary
        assert "max pairwise distance" in summary
        assert "0.420" in summary
        assert "0.670" in summary
        assert "gpt-4o" in summary
        assert "claude-opus-4-6" in summary

    def test_drift_summary(self) -> None:
        trigger = _make_trigger(
            trigger_type=TriggerType.DRIFT,
            domain_slug=None,
            model_id=None,
            evidence={
                "model_version_returned": "claude-opus-4-6-20260101",
                "procrustes_distance": 0.182,
                "date_pair": ["2026-01-01", "2026-03-01"],
            },
        )
        summary = _cli.format_trigger_summary(trigger)
        assert "Procrustes distance" in summary
        assert "0.182" in summary
        assert "2026-01-01" in summary
        assert "2026-03-01" in summary

    def test_monthly_roundup_summary(self) -> None:
        trigger = _make_trigger(
            trigger_type=TriggerType.MONTHLY_ROUNDUP,
            domain_slug=None,
            model_id=None,
            evidence={"month": "2026-05"},
        )
        summary = _cli.format_trigger_summary(trigger)
        assert "2026-05" in summary
        # §5.11 binding: T1 §5.7-compliant phrasing at display layer.
        assert "monthly cross-domain categorical-structure roundup" in summary.lower()


# ─────────────────────────────────────────────────────────────────────────────
# TestDraftSelfRatingLabel
# ─────────────────────────────────────────────────────────────────────────────


class TestDraftSelfRatingLabel:
    """§5.1 — Display contains 'Drafter self-rating' and NOT 'Confidence'."""

    def test_drafter_self_rating_label_present(self, capsys: pytest.CaptureFixture) -> None:
        draft = _make_draft(drafter_self_rating=0.75)
        _cli._display_draft(draft, 1, 1)
        captured = capsys.readouterr()
        assert "Drafter self-rating" in captured.out

    def test_confidence_label_absent(self, capsys: pytest.CaptureFixture) -> None:
        """The word 'Confidence' must NOT appear as a standalone label."""
        draft = _make_draft(drafter_self_rating=0.75)
        _cli._display_draft(draft, 1, 1)
        captured = capsys.readouterr()
        # "Confidence" must not appear as a field label in the display.
        # (It may appear in other contexts, but the label line must not start with it.)
        label_lines = [
            line.strip() for line in captured.out.splitlines()
            if line.strip().startswith("Confidence")
        ]
        assert label_lines == [], f"Found 'Confidence' label lines: {label_lines}"

    def test_self_rating_formatted_to_two_decimal_places(
        self, capsys: pytest.CaptureFixture
    ) -> None:
        """Drafter self-rating is displayed to two decimal places (e.g. 0.50)."""
        draft = _make_draft(drafter_self_rating=0.5)
        _cli._display_draft(draft, 1, 1)
        captured = capsys.readouterr()
        assert "0.50" in captured.out


# ─────────────────────────────────────────────────────────────────────────────
# TestFramingChecksDisplay
# ─────────────────────────────────────────────────────────────────────────────


class TestFramingChecksDisplay:
    """§5.2 — Canonical keys verbatim; extra keys below; pass/fail symbols correct."""

    def test_four_canonical_keys_displayed(self, capsys: pytest.CaptureFixture) -> None:
        draft = _make_draft()
        _cli._display_draft(draft, 1, 1)
        out = capsys.readouterr().out

        for key in _cli._CANONICAL_FRAMING_CHECK_KEYS:
            assert key in out, f"Expected canonical key {key!r} in output."

    def test_pass_symbol_for_true(self, capsys: pytest.CaptureFixture) -> None:
        draft = _make_draft()
        _cli._display_draft(draft, 1, 1)
        out = capsys.readouterr().out
        assert _cli._PASS_SYMBOL in out

    def test_fail_symbol_for_false(self, capsys: pytest.CaptureFixture) -> None:
        draft = _make_draft(
            framing_checks={
                "hypothesis_framing": False,
                "cognition_attribution": True,
                "bare_numeric_without_ci": True,
                "register_boundary": True,
            },
            framing_check_passed=False,
        )
        _cli._display_draft(draft, 1, 1)
        out = capsys.readouterr().out
        assert _cli._FAIL_SYMBOL in out

    def test_x_specific_extra_keys_displayed(self, capsys: pytest.CaptureFixture) -> None:
        """X-specific framing check keys are displayed below the four canonical keys."""
        extra_checks = {
            "hypothesis_framing": True,
            "cognition_attribution": True,
            "bare_numeric_without_ci": True,
            "register_boundary": True,
            "x_hook_has_measurement_noun": True,
            "x_hook_has_ci_shape": True,
            "x_hook_no_intent_attribution": True,
        }
        draft = _make_draft(framing_checks=extra_checks)
        _cli._display_draft(draft, 1, 1)
        out = capsys.readouterr().out

        for key in (
            "x_hook_has_measurement_noun",
            "x_hook_has_ci_shape",
            "x_hook_no_intent_attribution",
        ):
            assert key in out, f"Expected X-specific key {key!r} in output."

    def test_linkedin_extra_key_displayed(self, capsys: pytest.CaptureFixture) -> None:
        """LinkedIn-specific framing check key displayed below canonical four."""
        extra_checks = {
            "hypothesis_framing": True,
            "cognition_attribution": True,
            "bare_numeric_without_ci": True,
            "register_boundary": True,
            "linkedin_no_thought_leadership": True,
        }
        draft = _make_draft(framing_checks=extra_checks)
        _cli._display_draft(draft, 1, 1)
        out = capsys.readouterr().out
        assert "linkedin_no_thought_leadership" in out

    def test_bug_flag_on_nonempty_forbidden_terms(
        self, capsys: pytest.CaptureFixture
    ) -> None:
        """[BUG] appears when forbidden_terms_hit is non-empty (§5.9)."""
        draft = _make_draft()
        # Manually set forbidden_terms_hit to non-empty (queue-contract violation).
        draft_with_bug = draft.model_copy(
            update={"forbidden_terms_hit": ["worldview"]}
        )
        _cli._display_draft(draft_with_bug, 1, 1)
        out = capsys.readouterr().out
        assert "[BUG]" in out


# ─────────────────────────────────────────────────────────────────────────────
# TestRejectFlow
# ─────────────────────────────────────────────────────────────────────────────


class TestRejectFlow:
    """§5.3 — Five-code enum reason prompt; sidecar JSON; re-prompts on invalid."""

    def test_reject_moves_to_failed(
        self, queue_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        draft = _make_draft("draft_rej01")
        _save_pending(draft, queue_root)

        inputs = iter(["n", "forbidden_vocab", ""])
        monkeypatch.setattr("builtins.input", lambda _="": next(inputs))

        with patch("sys.stdout", new_callable=StringIO):
            _cli._run_review(queue_root)

        failed_path = queue_root / "failed" / "draft_rej01.json"
        assert failed_path.exists(), "Draft should be in failed/ after rejection."

    def test_reject_writes_sidecar_json(
        self, queue_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        draft = _make_draft("draft_rej02")
        _save_pending(draft, queue_root)

        inputs = iter(["n", "off_topic", "Not relevant to current audience"])
        monkeypatch.setattr("builtins.input", lambda _="": next(inputs))

        with patch("sys.stdout", new_callable=StringIO):
            _cli._run_review(queue_root)

        sidecar = queue_root / "failed" / "draft_rej02.reason.json"
        assert sidecar.exists(), "Sidecar JSON should be written on rejection."

        data = json.loads(sidecar.read_text(encoding="utf-8"))
        assert data["rejection_reason"] == "off_topic"
        assert data["free_text_note"] == "Not relevant to current audience"
        assert "rejected_at" in data

    def test_reject_sidecar_no_note(
        self, queue_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        draft = _make_draft("draft_rej03")
        _save_pending(draft, queue_root)

        inputs = iter(["n", "bare_numeric", ""])
        monkeypatch.setattr("builtins.input", lambda _="": next(inputs))

        with patch("sys.stdout", new_callable=StringIO):
            _cli._run_review(queue_root)

        sidecar = queue_root / "failed" / "draft_rej03.reason.json"
        data = json.loads(sidecar.read_text(encoding="utf-8"))
        assert data["rejection_reason"] == "bare_numeric"
        assert data["free_text_note"] is None

    def test_invalid_reason_re_prompts(
        self, queue_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """An invalid reason code causes re-prompt; valid code eventually accepted."""
        draft = _make_draft("draft_rej04")
        _save_pending(draft, queue_root)

        # First rejection reason is invalid; second is valid.
        inputs = iter(["n", "invalid_code", "other", "documenting a bypass"])
        monkeypatch.setattr("builtins.input", lambda _="": next(inputs))

        with patch("sys.stdout", new_callable=StringIO):
            _cli._run_review(queue_root)

        sidecar = queue_root / "failed" / "draft_rej04.reason.json"
        assert sidecar.exists()
        data = json.loads(sidecar.read_text(encoding="utf-8"))
        assert data["rejection_reason"] == "other"

    def test_all_five_codes_accepted(self, queue_root: Path) -> None:
        """All five rejection codes are in the REJECTION_CODES tuple."""
        assert "forbidden_vocab" in _cli.REJECTION_CODES
        assert "register_boundary" in _cli.REJECTION_CODES
        assert "bare_numeric" in _cli.REJECTION_CODES
        assert "off_topic" in _cli.REJECTION_CODES
        assert "other" in _cli.REJECTION_CODES
        assert len(_cli.REJECTION_CODES) == 5


# ─────────────────────────────────────────────────────────────────────────────
# TestEditFlowPasses
# ─────────────────────────────────────────────────────────────────────────────


class TestEditFlowPasses:
    """§5.4/§5.5 — Editor pass: draft moves to approved/; text_history appended."""

    def test_edit_pass_moves_to_approved(
        self, queue_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        original_text = "Original corpus-lens post text."
        draft = _make_draft("draft_ep01", text=original_text)
        _save_pending(draft, queue_root)

        edited_text = "Edited corpus-lens post text with CI (95% CI [0.3, 0.7])."

        def mock_open_editor(buffer: str) -> str:
            return edited_text

        monkeypatch.setattr(_cli, "_open_editor", mock_open_editor)
        inputs = iter(["e"])
        monkeypatch.setattr("builtins.input", lambda _="": next(inputs))

        with patch("sys.stdout", new_callable=StringIO):
            _cli._run_review(queue_root)

        approved_path = queue_root / "approved" / "draft_ep01.json"
        assert approved_path.exists(), "Draft should be in approved/ after passing edit."

    def test_text_history_appended_on_edit_pass(
        self, queue_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        original_text = "Original text for history test."
        draft = _make_draft("draft_ep02", text=original_text)
        _save_pending(draft, queue_root)

        edited_text = "Edited text with CI (95% CI [0.3, 0.7])."

        monkeypatch.setattr(_cli, "_open_editor", lambda buf: edited_text)
        inputs = iter(["e"])
        monkeypatch.setattr("builtins.input", lambda _="": next(inputs))

        with patch("sys.stdout", new_callable=StringIO):
            _cli._run_review(queue_root)

        approved_path = queue_root / "approved" / "draft_ep02.json"
        loaded = load_draft(approved_path)
        assert original_text in loaded.text_history, (
            "Original text should be appended to text_history on approved edit."
        )
        assert loaded.text == edited_text

    def test_edit_preamble_stripped(self) -> None:
        """Lines beginning with '#' are stripped before validation (§5.4)."""
        raw = (
            "# LSB Social Draft Editor\n"
            "# Some preamble comment.\n"
            "Actual post content goes here.\n"
        )
        stripped = _cli._strip_preamble(raw)
        assert "# LSB Social Draft Editor" not in stripped
        assert "Actual post content goes here." in stripped


# ─────────────────────────────────────────────────────────────────────────────
# TestEditFlowFails
# ─────────────────────────────────────────────────────────────────────────────


class TestEditFlowFails:
    """§5.5 — Validator-as-subject wording; draft returns to pending/."""

    def test_failed_edit_uses_validator_as_subject_wording(
        self, queue_root: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
    ) -> None:
        """Failure display says 'Edit did not pass validator.' (not operator-shaming)."""
        draft = _make_draft("draft_ef01")
        _save_pending(draft, queue_root)

        # This text contains "worldview" which triggers cognition_attribution failure.
        bad_edit = "This model's worldview organises family terms."

        monkeypatch.setattr(_cli, "_open_editor", lambda buf: bad_edit)
        # "e" triggers edit; bad_edit fails; "n" declines re-edit; "s" skips to end.
        inputs = iter(["e", "n", "s"])
        monkeypatch.setattr("builtins.input", lambda _="": next(inputs))

        _cli._run_review(queue_root)

        out = capsys.readouterr().out
        assert "Edit did not pass validator." in out, (
            "Failure message must say 'Edit did not pass validator.' (validator-as-subject)."
        )

    def test_no_operator_shaming_wording(
        self, queue_root: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
    ) -> None:
        """Forbidden wording ('Your edit violates', 'Bad edit', 'you wrote') absent."""
        draft = _make_draft("draft_ef02")
        _save_pending(draft, queue_root)

        bad_edit = "Model X worldview on food categories."

        monkeypatch.setattr(_cli, "_open_editor", lambda buf: bad_edit)
        inputs = iter(["e", "n", "s"])  # fail; decline re-edit; skip
        monkeypatch.setattr("builtins.input", lambda _="": next(inputs))

        _cli._run_review(queue_root)

        out = capsys.readouterr().out
        forbidden_phrases = [
            "You wrote forbidden",
            "Your edit violates",
            "Bad edit",
            "you wrote forbidden",
        ]
        for phrase in forbidden_phrases:
            assert phrase not in out, (
                f"Operator-shaming phrase {phrase!r} must not appear in edit-failure output."
            )

    def test_failed_edit_stays_in_pending(
        self, queue_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """After a failed edit + user declines re-edit, draft remains in pending/."""
        draft = _make_draft("draft_ef03")
        _save_pending(draft, queue_root)

        bad_edit = "The model's worldview on family structures."

        monkeypatch.setattr(_cli, "_open_editor", lambda buf: bad_edit)
        inputs = iter(["e", "n", "s"])  # fail edit, decline re-edit, then skip
        monkeypatch.setattr("builtins.input", lambda _="": next(inputs))

        with patch("sys.stdout", new_callable=StringIO):
            _cli._run_review(queue_root)

        pending_path = queue_root / "pending" / "draft_ef03.json"
        assert pending_path.exists(), (
            "Draft should remain in pending/ after failed edit + decline re-edit."
        )

    def test_failed_edit_appends_to_text_history(
        self, queue_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Failed edit is appended to text_history; draft.text is unchanged."""
        original_text = "Original clean text."
        draft = _make_draft("draft_ef04", text=original_text)
        _save_pending(draft, queue_root)

        bad_edit = "Edited text with model worldview violation."

        monkeypatch.setattr(_cli, "_open_editor", lambda buf: bad_edit)
        inputs = iter(["e", "n", "s"])
        monkeypatch.setattr("builtins.input", lambda _="": next(inputs))

        with patch("sys.stdout", new_callable=StringIO):
            _cli._run_review(queue_root)

        pending_path = queue_root / "pending" / "draft_ef04.json"
        loaded = load_draft(pending_path)
        assert loaded.text == original_text, "draft.text must not be overwritten on failed edit."
        assert bad_edit in loaded.text_history, (
            "Failed edit should be appended to text_history for audit trail."
        )


# ─────────────────────────────────────────────────────────────────────────────
# TestApproveFlow
# ─────────────────────────────────────────────────────────────────────────────


class TestApproveFlow:
    """y → approved/."""

    def test_approve_moves_to_approved(
        self, queue_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        draft = _make_draft("draft_ap01")
        _save_pending(draft, queue_root)

        inputs = iter(["y"])
        monkeypatch.setattr("builtins.input", lambda _="": next(inputs))

        with patch("sys.stdout", new_callable=StringIO):
            _cli._run_review(queue_root)

        approved_path = queue_root / "approved" / "draft_ap01.json"
        pending_path = queue_root / "pending" / "draft_ap01.json"
        assert approved_path.exists(), "Draft should be in approved/."
        assert not pending_path.exists(), "Draft should be removed from pending/."

    def test_approve_content_intact(
        self, queue_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        draft = _make_draft("draft_ap02", text="Approve-flow test content.")
        _save_pending(draft, queue_root)

        inputs = iter(["y"])
        monkeypatch.setattr("builtins.input", lambda _="": next(inputs))

        with patch("sys.stdout", new_callable=StringIO):
            _cli._run_review(queue_root)

        approved = load_draft(queue_root / "approved" / "draft_ap02.json")
        assert approved.text == "Approve-flow test content."


# ─────────────────────────────────────────────────────────────────────────────
# TestSkipFlow
# ─────────────────────────────────────────────────────────────────────────────


class TestSkipFlow:
    """s → advance to next draft without state change."""

    def test_skip_leaves_draft_in_pending(
        self, queue_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        draft = _make_draft("draft_sk01")
        _save_pending(draft, queue_root)

        inputs = iter(["s"])
        monkeypatch.setattr("builtins.input", lambda _="": next(inputs))

        with patch("sys.stdout", new_callable=StringIO):
            _cli._run_review(queue_root)

        pending_path = queue_root / "pending" / "draft_sk01.json"
        assert pending_path.exists(), "Draft should remain in pending/ after skip."

    def test_skip_advances_to_next(
        self, queue_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Skip first draft; approve second draft."""
        base = datetime(2026, 5, 1, 0, 0, 0, tzinfo=UTC)
        d1 = _make_draft("draft_sk02", created_at=base)
        d2 = _make_draft("draft_sk03", created_at=base + timedelta(hours=1))
        _save_pending(d1, queue_root)
        _save_pending(d2, queue_root)

        inputs = iter(["s", "y"])
        monkeypatch.setattr("builtins.input", lambda _="": next(inputs))

        with patch("sys.stdout", new_callable=StringIO):
            _cli._run_review(queue_root)

        assert (queue_root / "pending" / "draft_sk02.json").exists(), "Skipped draft in pending."
        assert (queue_root / "approved" / "draft_sk03.json").exists(), "Approved draft in approved."


# ─────────────────────────────────────────────────────────────────────────────
# TestQuitFlow
# ─────────────────────────────────────────────────────────────────────────────


class TestQuitFlow:
    """q → stop; remaining drafts stay in pending/."""

    def test_quit_leaves_drafts_in_pending(
        self, queue_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        base = datetime(2026, 5, 1, 0, 0, 0, tzinfo=UTC)
        d1 = _make_draft("draft_q01", created_at=base)
        d2 = _make_draft("draft_q02", created_at=base + timedelta(hours=1))
        _save_pending(d1, queue_root)
        _save_pending(d2, queue_root)

        inputs = iter(["q"])
        monkeypatch.setattr("builtins.input", lambda _="": next(inputs))

        with patch("sys.stdout", new_callable=StringIO):
            _cli._run_review(queue_root)

        assert (queue_root / "pending" / "draft_q01.json").exists()
        assert (queue_root / "pending" / "draft_q02.json").exists()

    def test_quit_prints_remaining_count(
        self, queue_root: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
    ) -> None:
        """§5.6 — CLI prints 'Quit. {n} draft(s) remain in pending/' on exit."""
        base = datetime(2026, 5, 1, 0, 0, 0, tzinfo=UTC)
        for i in range(3):
            d = _make_draft(f"draft_q0{i+10}", created_at=base + timedelta(hours=i))
            _save_pending(d, queue_root)

        inputs = iter(["q"])
        monkeypatch.setattr("builtins.input", lambda _="": next(inputs))

        _cli._run_review(queue_root)

        out = capsys.readouterr().out
        assert "Quit." in out
        assert "remain in pending/" in out


# ─────────────────────────────────────────────────────────────────────────────
# TestMonthlyRoundupSummary
# ─────────────────────────────────────────────────────────────────────────────


class TestMonthlyRoundupSummary:
    """§5.7/§5.11 — MONTHLY_ROUNDUP uses the T1 §5.7-compliant phrasing."""

    def test_binding_wording_present(self) -> None:
        """Summary contains 'monthly cross-domain categorical-structure roundup'."""
        trigger = _make_trigger(
            trigger_type=TriggerType.MONTHLY_ROUNDUP,
            domain_slug=None,
            model_id=None,
            evidence={"month": "2026-05"},
        )
        summary = _cli.format_trigger_summary(trigger)
        assert "monthly cross-domain categorical-structure roundup" in summary.lower(), (
            "MONTHLY_ROUNDUP summary must use the T1 §5.7-compliant phrasing verbatim."
        )

    def test_month_string_included(self) -> None:
        trigger = _make_trigger(
            trigger_type=TriggerType.MONTHLY_ROUNDUP,
            domain_slug=None,
            model_id=None,
            evidence={"month": "2026-05"},
        )
        summary = _cli.format_trigger_summary(trigger)
        assert "2026-05" in summary

    def test_pre_amendment_phrasing_absent(self) -> None:
        """Pre-amendment 'state of cultural alignment' must not appear (§5.11)."""
        trigger = _make_trigger(
            trigger_type=TriggerType.MONTHLY_ROUNDUP,
            domain_slug=None,
            model_id=None,
            evidence={"month": "2026-05"},
        )
        summary = _cli.format_trigger_summary(trigger)
        assert "state of cultural alignment" not in summary.lower(), (
            "Pre-amendment phrasing must not appear per §5.11."
        )


# ─────────────────────────────────────────────────────────────────────────────
# TestDriftSummaryCaveat
# ─────────────────────────────────────────────────────────────────────────────


class TestDriftSummaryCaveat:
    """§5.7 — DRIFT summary includes the mandatory placeholder caveat."""

    def test_drift_caveat_present(self) -> None:
        """'threshold 0.15 placeholder' caveat must appear while lockout is engaged."""
        trigger = _make_trigger(
            trigger_type=TriggerType.DRIFT,
            domain_slug=None,
            model_id=None,
            evidence={
                "model_version_returned": "claude-opus-4-6-20260101",
                "procrustes_distance": 0.182,
                "date_pair": ["2026-01-01", "2026-03-01"],
            },
        )
        summary = _cli.format_trigger_summary(trigger)
        assert "threshold 0.15 placeholder" in summary, (
            "DRIFT summary must include 'threshold 0.15 placeholder' caveat while lockout engaged."
        )

    def test_drift_lockout_mention(self) -> None:
        """DRIFT summary mentions that drift trigger lockout is engaged."""
        trigger = _make_trigger(
            trigger_type=TriggerType.DRIFT,
            domain_slug=None,
            model_id=None,
            evidence={
                "model_version_returned": "gpt-5-turbo-20260101",
                "procrustes_distance": 0.21,
                "date_pair": ["2026-02-01", "2026-04-01"],
            },
        )
        summary = _cli.format_trigger_summary(trigger)
        assert "lockout" in summary.lower(), (
            "DRIFT summary must mention that the drift trigger lockout is engaged."
        )

    def test_procrustes_distance_verbatim(self) -> None:
        """Summary uses 'Procrustes distance' verbatim (Register-3 statistic)."""
        trigger = _make_trigger(
            trigger_type=TriggerType.DRIFT,
            domain_slug=None,
            model_id=None,
            evidence={
                "model_version_returned": "model-x-20260101",
                "procrustes_distance": 0.19,
                "date_pair": ["2026-01-01", "2026-02-01"],
            },
        )
        summary = _cli.format_trigger_summary(trigger)
        assert "Procrustes distance" in summary, (
            "DRIFT summary must use 'Procrustes distance' verbatim (Register-3)."
        )


# ─────────────────────────────────────────────────────────────────────────────
# TestDivergenceSummaryWording
# ─────────────────────────────────────────────────────────────────────────────


class TestDivergenceSummaryWording:
    """§5.7 — DIVERGENCE uses 'max pairwise distance' NOT 'pairwise gap'."""

    def test_max_pairwise_distance_present(self) -> None:
        trigger = _make_trigger(
            trigger_type=TriggerType.DIVERGENCE,
            domain_slug="food",
            model_id=None,
            evidence={
                "domain_slug": "food",
                "model_pair": ["gpt-4o", "claude-opus-4-6"],
                "old_high": 0.42,
                "new_high": 0.67,
                "gap_delta": 0.25,
            },
        )
        summary = _cli.format_trigger_summary(trigger)
        assert "max pairwise distance" in summary, (
            "DIVERGENCE summary must use 'max pairwise distance' (NOT 'pairwise gap')."
        )

    def test_pairwise_gap_not_used(self) -> None:
        """The phrase 'pairwise gap' must not appear in DIVERGENCE summary."""
        trigger = _make_trigger(
            trigger_type=TriggerType.DIVERGENCE,
            domain_slug="food",
            model_id=None,
            evidence={
                "domain_slug": "food",
                "model_pair": ["gpt-4o", "claude-opus-4-6"],
                "old_high": 0.42,
                "new_high": 0.67,
                "gap_delta": 0.25,
            },
        )
        summary = _cli.format_trigger_summary(trigger)
        assert "pairwise gap" not in summary.lower(), (
            "'pairwise gap' must NOT appear; use 'max pairwise distance' per §5.7."
        )

    def test_divergence_formatted_values(self) -> None:
        """Old/new highs and delta are formatted to 3 decimal places."""
        trigger = _make_trigger(
            trigger_type=TriggerType.DIVERGENCE,
            domain_slug="family",
            model_id=None,
            evidence={
                "domain_slug": "family",
                "model_pair": ["model-a", "model-b"],
                "old_high": 0.4,
                "new_high": 0.7,
                "gap_delta": 0.3,
            },
        )
        summary = _cli.format_trigger_summary(trigger)
        assert "0.400" in summary
        assert "0.700" in summary
