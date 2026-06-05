"""Unit tests for the LSB admin console Flask app — Phase 7 T6b.

Uses Flask test client; no real Anthropic API calls; no real Bluesky API calls.
All drafter calls are mocked; all queue operations use a tmp_path fixture.

Test classes:
  TestLoopbackBindEnforcement    — startup log contains loopback-only message
  TestIndexRoute                 — GET / returns 200 with queue counts
  TestTriggersList               — GET /triggers returns 200 with detected triggers
  TestDraftRequestFlow           — confirm page → POST → draft saved → redirect
  TestDraftRequestWithDrafterReject — POST triggers DrafterRejectedException
  TestApproveFlow                — GET shows confirm; POST moves pending→approved
  TestRejectFlow                 — GET shows form; POST moves pending→failed + sidecar
  TestEditFlowPasses             — edited text passes validator → approved
  TestEditFlowFails              — edited text fails validator → pending with history
  TestPublishFlow                — confirm wording; POST invokes publisher
  TestCSRFProtection             — POST without token → 403
  TestForbiddenVocabAbsent       — rendered HTML has no forbidden phrases
  TestBindingWordingPresent      — trigger summaries contain binding wording
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from cdb_core.schemas import (
    Platform,
    PublishStatus,
    SocialDraft,
    SocialPostRecord,
    SocialTrigger,
    TriggerType,
)
from cdb_social.admin_console.app import create_app
from cdb_social.publisher import PublisherNotEnabled

# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────


def _make_trigger(
    trigger_type: TriggerType = TriggerType.DIVERGENCE,
    domain_slug: str | None = "family",
    model_id: str | None = "gpt-4",
    evidence: dict | None = None,
    dedupe_key: str = "abcdef0123456789",
) -> SocialTrigger:
    if evidence is None:
        evidence = {
            "model_pair": ["gpt-4", "claude-3"],
            "old_high": 0.72,
            "new_high": 0.85,
            "gap_delta": 0.13,
            "domain_slug": "family",
        }
    return SocialTrigger(
        trigger_type=trigger_type,
        detected_at=datetime(2026, 5, 17, 10, 0, 0, tzinfo=UTC),
        domain_slug=domain_slug,
        model_id=model_id,
        evidence=evidence,
        dedupe_key=dedupe_key,
    )


def _make_draft(
    draft_id: str = "draftid1234abcd",
    platform: Platform = Platform.BLUESKY,
    trigger: SocialTrigger | None = None,
    text: str = "LSB categorical structure in the family domain (95% CI [0.70, 0.90]).",
    framing_checks: dict | None = None,
    framing_check_passed: bool = True,
) -> SocialDraft:
    if trigger is None:
        trigger = _make_trigger()
    if framing_checks is None:
        framing_checks = {
            "hypothesis_framing": True,
            "cognition_attribution": True,
            "bare_numeric_without_ci": True,
            "register_boundary": True,
        }
    return SocialDraft(
        draft_id=draft_id,
        trigger=trigger,
        platform=platform,
        text=text,
        suggested_posting_time=datetime(2026, 5, 19, 14, 0, 0, tzinfo=UTC),
        drafter_self_rating=0.5,
        methodology_url="https://cogstructurelab.com/family",
        dashboard_url="https://cogstructurelab.com/family",
        framing_check_passed=framing_check_passed,
        framing_checks=framing_checks,
        drafter_version="bluesky-v1",
        prompt_version="v1",
        created_at=datetime(2026, 5, 17, 10, 30, 0, tzinfo=UTC),
    )


def _write_detected_triggers(state_dir: Path, triggers: list[SocialTrigger]) -> None:
    """Write detected_triggers.json — the source read by _load_detected_triggers.

    cmd_detect writes this file after a successful digest send.  Tests use this
    helper to pre-populate the admin console's trigger list without running
    cmd_detect (which would need state files and email config).
    """
    state_dir.mkdir(parents=True, exist_ok=True)
    data = {
        "triggers": [json.loads(t.model_dump_json()) for t in triggers],
    }
    (state_dir / "detected_triggers.json").write_text(
        json.dumps(data, indent=2), encoding="utf-8"
    )


def _write_draft_to_queue(draft: SocialDraft, state: str, queue_root: Path) -> Path:
    """Write a draft JSON file to the given queue state directory."""
    state_dir = queue_root / state
    state_dir.mkdir(parents=True, exist_ok=True)
    path = state_dir / f"{draft.draft_id}.json"
    path.write_text(draft.model_dump_json(indent=2), encoding="utf-8")
    return path


@pytest.fixture
def tmp_queue_root(tmp_path: Path) -> Path:
    """Temporary queue root with all state directories."""
    queue_root = tmp_path / "queue"
    for state in ("pending", "approved", "published", "failed"):
        (queue_root / state).mkdir(parents=True)
    return queue_root


@pytest.fixture
def tmp_state_dir(tmp_path: Path) -> Path:
    """Temporary state directory."""
    state_dir = tmp_path / "state"
    state_dir.mkdir(parents=True)
    return state_dir


@pytest.fixture
def app(tmp_queue_root: Path, tmp_state_dir: Path, monkeypatch: pytest.MonkeyPatch):
    """Create a Flask test app with temp directories."""
    monkeypatch.setenv("LSB_SOCIAL_QUEUE_ROOT", str(tmp_queue_root))
    monkeypatch.setenv("LSB_SOCIAL_STATE_DIR", str(tmp_state_dir))
    monkeypatch.setenv("BLUESKY_HANDLE", "testhandle.bsky.social")
    monkeypatch.setenv("BLUESKY_APP_PASSWORD", "test-app-password-xxxx")
    flask_app = create_app()
    flask_app.config["TESTING"] = True
    return flask_app


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


# ─────────────────────────────────────────────────────────────────────────────
# TestLoopbackBindEnforcement
# ─────────────────────────────────────────────────────────────────────────────


class TestLoopbackBindEnforcement:
    """The startup log confirms loopback-only bind."""

    def test_startup_log_contains_loopback_message(self) -> None:
        """Running python -m cdb_social.admin_console --help type invocation shows loopback."""
        # We test that __main__.py contains the hardcoded loopback address and message.
        import importlib.util

        spec = importlib.util.find_spec("cdb_social.admin_console.__main__")
        assert spec is not None
        source_path = spec.origin
        assert source_path is not None
        source = Path(source_path).read_text(encoding="utf-8")
        assert "127.0.0.1:8000 (loopback only; no internet exposure)" in source, (
            "Startup log message not found in __main__.py"
        )

    def test_hardcoded_host_is_loopback(self) -> None:
        """__main__.py hardcodes 127.0.0.1 as the bind address."""
        import importlib.util

        spec = importlib.util.find_spec("cdb_social.admin_console.__main__")
        assert spec is not None
        source = Path(spec.origin).read_text(encoding="utf-8")
        assert 'host = "127.0.0.1"' in source
        # argparse / add_argument for --host must not appear
        assert "add_argument" not in source, "No CLI argument parsing for --host"


# ─────────────────────────────────────────────────────────────────────────────
# TestIndexRoute
# ─────────────────────────────────────────────────────────────────────────────


class TestIndexRoute:
    """GET / returns 200 with queue counts."""

    def test_index_returns_200(self, client) -> None:
        rv = client.get("/")
        assert rv.status_code == 200

    def test_index_contains_queue_states(self, client) -> None:
        rv = client.get("/")
        html = rv.data.decode("utf-8")
        assert "pending" in html
        assert "approved" in html
        assert "published" in html
        assert "failed" in html

    def test_index_shows_nav_links(self, client) -> None:
        rv = client.get("/")
        html = rv.data.decode("utf-8")
        assert "Triggers" in html
        assert "/triggers" in html

    def test_index_with_pending_draft_shows_count(
        self, client, tmp_queue_root: Path
    ) -> None:
        draft = _make_draft()
        _write_draft_to_queue(draft, "pending", tmp_queue_root)
        rv = client.get("/")
        html = rv.data.decode("utf-8")
        assert "1" in html


# ─────────────────────────────────────────────────────────────────────────────
# TestTriggersList
# ─────────────────────────────────────────────────────────────────────────────


class TestTriggersList:
    """GET /triggers returns 200 and lists detected triggers."""

    def test_triggers_list_returns_200(self, client) -> None:
        rv = client.get("/triggers")
        assert rv.status_code == 200

    def test_triggers_list_shows_draft_via_llm_button(
        self, client, tmp_state_dir: Path
    ) -> None:
        trigger = _make_trigger()
        _write_detected_triggers(tmp_state_dir, [trigger])
        rv = client.get("/triggers")
        html = rv.data.decode("utf-8")
        assert "Draft via LLM" in html

    def test_triggers_list_shows_trigger_summary(
        self, client, tmp_state_dir: Path
    ) -> None:
        trigger = _make_trigger(trigger_type=TriggerType.DIVERGENCE)
        _write_detected_triggers(tmp_state_dir, [trigger])
        rv = client.get("/triggers")
        html = rv.data.decode("utf-8")
        # DIVERGENCE summary uses "max pairwise distance" (binding wording)
        assert "max pairwise distance" in html

    def test_triggers_list_no_forbidden_vocab(
        self, client, tmp_state_dir: Path
    ) -> None:
        trigger = _make_trigger()
        _write_detected_triggers(tmp_state_dir, [trigger])
        rv = client.get("/triggers")
        html = rv.data.decode("utf-8").lower()
        assert "state of cultural alignment" not in html
        assert "pairwise gap" not in html


# ─────────────────────────────────────────────────────────────────────────────
# TestDraftRequestFlow
# ─────────────────────────────────────────────────────────────────────────────


class TestDraftRequestFlow:
    """GET /triggers/<key>/draft shows confirmation; POST invokes drafter."""

    def test_get_shows_confirmation_page(
        self, client, tmp_state_dir: Path
    ) -> None:
        trigger = _make_trigger()
        _write_detected_triggers(tmp_state_dir, [trigger])
        rv = client.get(
            f"/triggers/{trigger.dedupe_key}/draft?platform=bluesky"
        )
        assert rv.status_code == 200
        html = rv.data.decode("utf-8")
        assert "Draft via LLM?" in html
        assert "Yes, draft via LLM" in html
        # Must NOT contain token-count/cost display per CDA SME §5.3 R14
        assert "est. tokens" not in html
        assert "tokens" not in html.lower() or "csrf_token" in html.lower()

    def test_get_confirm_no_token_count_display(
        self, client, tmp_state_dir: Path
    ) -> None:
        """Confirmation page must not display token count per R14."""
        trigger = _make_trigger()
        _write_detected_triggers(tmp_state_dir, [trigger])
        rv = client.get(
            f"/triggers/{trigger.dedupe_key}/draft?platform=bluesky"
        )
        html = rv.data.decode("utf-8").lower()
        assert "est. tokens" not in html
        assert "expected cost" not in html
        assert "~$" not in html

    def test_post_invokes_drafter_and_redirects(
        self, client, tmp_state_dir: Path, tmp_queue_root: Path
    ) -> None:
        trigger = _make_trigger()
        _write_detected_triggers(tmp_state_dir, [trigger])

        draft = _make_draft(trigger=trigger)
        mock_drafter = MagicMock()
        mock_drafter.draft.return_value = draft

        with patch(
            "cdb_social.admin_console.routes._make_drafter", return_value=mock_drafter
        ), patch(
            "cdb_social.admin_console.routes._load_domain_result_for_trigger",
            return_value=MagicMock(),
        ):
            # Get CSRF token first
            rv_get = client.get(
                f"/triggers/{trigger.dedupe_key}/draft?platform=bluesky"
            )
            assert rv_get.status_code == 200

            with client.session_transaction() as sess:
                csrf_token = sess.get("csrf_token", "")

            post_rv = client.post(
                f"/triggers/{trigger.dedupe_key}/draft?platform=bluesky",
                data={"csrf_token": csrf_token},
                follow_redirects=False,
            )

        assert post_rv.status_code == 302
        location = post_rv.headers.get("Location", "")
        assert f"/draft/{draft.draft_id}" in location

    def test_post_saves_draft_to_pending(
        self, client, tmp_state_dir: Path, tmp_queue_root: Path
    ) -> None:
        trigger = _make_trigger()
        _write_detected_triggers(tmp_state_dir, [trigger])
        draft = _make_draft(trigger=trigger)
        mock_drafter = MagicMock()
        mock_drafter.draft.return_value = draft

        with patch(
            "cdb_social.admin_console.routes._make_drafter", return_value=mock_drafter
        ), patch(
            "cdb_social.admin_console.routes._load_domain_result_for_trigger",
            return_value=MagicMock(),
        ):
            client.get(
                f"/triggers/{trigger.dedupe_key}/draft?platform=bluesky"
            )
            with client.session_transaction() as sess:
                csrf_token = sess.get("csrf_token", "")
            client.post(
                f"/triggers/{trigger.dedupe_key}/draft?platform=bluesky",
                data={"csrf_token": csrf_token},
                follow_redirects=True,
            )

        pending_path = tmp_queue_root / "pending" / f"{draft.draft_id}.json"
        assert pending_path.exists()

    def test_post_unknown_trigger_returns_404(
        self, client, tmp_state_dir: Path
    ) -> None:
        _write_detected_triggers(tmp_state_dir, [])
        rv = client.get("/triggers/nonexistent0000/draft?platform=bluesky")
        assert rv.status_code == 404


# ─────────────────────────────────────────────────────────────────────────────
# TestDraftRequestWithDrafterReject
# ─────────────────────────────────────────────────────────────────────────────


class TestDraftRequestWithDrafterReject:
    """POST that triggers DrafterRejectedException renders error page."""

    def test_drafter_rejection_renders_error_page(
        self, client, tmp_state_dir: Path, tmp_queue_root: Path
    ) -> None:
        from cdb_social.drafters.base import DrafterRejectedException

        trigger = _make_trigger()
        _write_detected_triggers(tmp_state_dir, [trigger])
        mock_drafter = MagicMock()
        mock_drafter.draft.side_effect = DrafterRejectedException(
            "Draft rejected: forbidden vocab",
            draft_text="Model X believes this.",
            forbidden_terms_hit=["believes"],
            hypothesis_patterns_hit=[],
            bare_numerics=[],
        )

        with patch(
            "cdb_social.admin_console.routes._make_drafter", return_value=mock_drafter
        ), patch(
            "cdb_social.admin_console.routes._load_domain_result_for_trigger",
            return_value=MagicMock(),
        ):
            client.get(
                f"/triggers/{trigger.dedupe_key}/draft?platform=bluesky"
            )
            with client.session_transaction() as sess:
                csrf_token = sess.get("csrf_token", "")
            rv = client.post(
                f"/triggers/{trigger.dedupe_key}/draft?platform=bluesky",
                data={"csrf_token": csrf_token},
            )

        html = rv.data.decode("utf-8")
        # §5.4 binding wording
        assert "Drafter call did not pass validator" in html
        assert "No draft was created" in html
        assert "guardrail, not an operator error" in html
        assert "believes" in html

    def test_drafter_rejection_shows_forbidden_terms(
        self, client, tmp_state_dir: Path, tmp_queue_root: Path
    ) -> None:
        from cdb_social.drafters.base import DrafterRejectedException

        trigger = _make_trigger()
        _write_detected_triggers(tmp_state_dir, [trigger])
        mock_drafter = MagicMock()
        mock_drafter.draft.side_effect = DrafterRejectedException(
            "rejected",
            draft_text="...",
            forbidden_terms_hit=["worldview", "believes"],
            hypothesis_patterns_hit=["this proves"],
            bare_numerics=[],
        )

        with patch(
            "cdb_social.admin_console.routes._make_drafter", return_value=mock_drafter
        ), patch(
            "cdb_social.admin_console.routes._load_domain_result_for_trigger",
            return_value=MagicMock(),
        ):
            client.get(
                f"/triggers/{trigger.dedupe_key}/draft?platform=bluesky"
            )
            with client.session_transaction() as sess:
                csrf_token = sess.get("csrf_token", "")
            rv = client.post(
                f"/triggers/{trigger.dedupe_key}/draft?platform=bluesky",
                data={"csrf_token": csrf_token},
            )

        html = rv.data.decode("utf-8")
        assert "worldview" in html
        assert "believes" in html

    def test_drafter_rejection_does_not_create_draft_file(
        self, client, tmp_state_dir: Path, tmp_queue_root: Path
    ) -> None:
        from cdb_social.drafters.base import DrafterRejectedException

        trigger = _make_trigger()
        _write_detected_triggers(tmp_state_dir, [trigger])
        mock_drafter = MagicMock()
        mock_drafter.draft.side_effect = DrafterRejectedException(
            "rejected",
            draft_text="...",
        )

        with patch(
            "cdb_social.admin_console.routes._make_drafter", return_value=mock_drafter
        ), patch(
            "cdb_social.admin_console.routes._load_domain_result_for_trigger",
            return_value=MagicMock(),
        ):
            client.get(
                f"/triggers/{trigger.dedupe_key}/draft?platform=bluesky"
            )
            with client.session_transaction() as sess:
                csrf_token = sess.get("csrf_token", "")
            client.post(
                f"/triggers/{trigger.dedupe_key}/draft?platform=bluesky",
                data={"csrf_token": csrf_token},
            )

        pending_files = list((tmp_queue_root / "pending").glob("*.json"))
        assert len(pending_files) == 0


# ─────────────────────────────────────────────────────────────────────────────
# TestApproveFlow
# ─────────────────────────────────────────────────────────────────────────────


class TestApproveFlow:
    """GET shows confirmation; POST moves pending→approved."""

    def test_get_approve_shows_confirmation(
        self, client, tmp_queue_root: Path
    ) -> None:
        draft = _make_draft()
        _write_draft_to_queue(draft, "pending", tmp_queue_root)
        rv = client.get(f"/draft/{draft.draft_id}/approve")
        assert rv.status_code == 200
        html = rv.data.decode("utf-8")
        assert "Approve draft?" in html
        assert "Yes, approve" in html

    def test_approve_confirm_says_does_not_publish(
        self, client, tmp_queue_root: Path
    ) -> None:
        """Per CDA SME §5.3 binding: confirmation body must say 'This does not publish.'"""
        draft = _make_draft()
        _write_draft_to_queue(draft, "pending", tmp_queue_root)
        rv = client.get(f"/draft/{draft.draft_id}/approve")
        html = rv.data.decode("utf-8")
        assert "This does not publish" in html

    def test_post_approve_moves_to_approved(
        self, client, tmp_queue_root: Path
    ) -> None:
        draft = _make_draft()
        _write_draft_to_queue(draft, "pending", tmp_queue_root)

        client.get(f"/draft/{draft.draft_id}/approve")
        with client.session_transaction() as sess:
            csrf_token = sess.get("csrf_token", "")

        post_rv = client.post(
            f"/draft/{draft.draft_id}/approve",
            data={"csrf_token": csrf_token},
            follow_redirects=False,
        )
        assert post_rv.status_code == 302
        # Draft should now be in approved/
        assert (tmp_queue_root / "approved" / f"{draft.draft_id}.json").exists()
        assert not (tmp_queue_root / "pending" / f"{draft.draft_id}.json").exists()

    def test_approve_non_pending_draft_returns_400(
        self, client, tmp_queue_root: Path
    ) -> None:
        draft = _make_draft()
        _write_draft_to_queue(draft, "approved", tmp_queue_root)
        rv = client.get(f"/draft/{draft.draft_id}/approve")
        assert rv.status_code == 400


# ─────────────────────────────────────────────────────────────────────────────
# TestRejectFlow
# ─────────────────────────────────────────────────────────────────────────────


class TestRejectFlow:
    """GET shows enum + free-text form; POST moves pending→failed + sidecar."""

    def test_get_reject_shows_form(self, client, tmp_queue_root: Path) -> None:
        draft = _make_draft()
        _write_draft_to_queue(draft, "pending", tmp_queue_root)
        rv = client.get(f"/draft/{draft.draft_id}/reject")
        assert rv.status_code == 200
        html = rv.data.decode("utf-8")
        assert "Reject draft?" in html
        assert "forbidden_vocab" in html
        assert "register_boundary" in html
        assert "bare_numeric" in html
        assert "off_topic" in html
        assert "other" in html

    def test_reject_form_has_free_text_area(
        self, client, tmp_queue_root: Path
    ) -> None:
        draft = _make_draft()
        _write_draft_to_queue(draft, "pending", tmp_queue_root)
        rv = client.get(f"/draft/{draft.draft_id}/reject")
        html = rv.data.decode("utf-8")
        assert "<textarea" in html

    def test_post_reject_moves_to_failed(
        self, client, tmp_queue_root: Path
    ) -> None:
        draft = _make_draft()
        _write_draft_to_queue(draft, "pending", tmp_queue_root)

        client.get(f"/draft/{draft.draft_id}/reject")
        with client.session_transaction() as sess:
            csrf_token = sess.get("csrf_token", "")

        post_rv = client.post(
            f"/draft/{draft.draft_id}/reject",
            data={"csrf_token": csrf_token, "reason": "off_topic", "note": "test note"},
            follow_redirects=False,
        )
        assert post_rv.status_code == 302
        assert (tmp_queue_root / "failed" / f"{draft.draft_id}.json").exists()
        assert not (tmp_queue_root / "pending" / f"{draft.draft_id}.json").exists()

    def test_post_reject_writes_sidecar_json(
        self, client, tmp_queue_root: Path
    ) -> None:
        draft = _make_draft()
        _write_draft_to_queue(draft, "pending", tmp_queue_root)

        client.get(f"/draft/{draft.draft_id}/reject")
        with client.session_transaction() as sess:
            csrf_token = sess.get("csrf_token", "")

        client.post(
            f"/draft/{draft.draft_id}/reject",
            data={"csrf_token": csrf_token, "reason": "forbidden_vocab", "note": ""},
        )

        sidecar_path = tmp_queue_root / "failed" / f"{draft.draft_id}.reject.json"
        assert sidecar_path.exists()
        sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
        assert sidecar["reason"] == "forbidden_vocab"
        assert sidecar["draft_id"] == draft.draft_id


# ─────────────────────────────────────────────────────────────────────────────
# TestEditFlowPasses
# ─────────────────────────────────────────────────────────────────────────────


class TestEditFlowPasses:
    """Edited text passes validator → approved state."""

    def test_edit_form_shows_current_text(
        self, client, tmp_queue_root: Path
    ) -> None:
        draft = _make_draft(text="Original text with CI (95% CI [0.5, 0.9]).")
        _write_draft_to_queue(draft, "pending", tmp_queue_root)
        rv = client.get(f"/draft/{draft.draft_id}/edit")
        assert rv.status_code == 200
        html = rv.data.decode("utf-8")
        assert "Original text with CI" in html

    def test_valid_edit_moves_to_approved(
        self, client, tmp_queue_root: Path
    ) -> None:
        draft = _make_draft()
        _write_draft_to_queue(draft, "pending", tmp_queue_root)

        client.get(f"/draft/{draft.draft_id}/edit")
        with client.session_transaction() as sess:
            csrf_token = sess.get("csrf_token", "")

        new_text = "Clean categorical structure output (95% CI [0.70, 0.90]) across domains."
        post_rv = client.post(
            f"/draft/{draft.draft_id}/edit",
            data={"csrf_token": csrf_token, "text": new_text, "action": "save"},
            follow_redirects=False,
        )
        assert post_rv.status_code == 302
        # Should be in approved
        assert (tmp_queue_root / "approved" / f"{draft.draft_id}.json").exists()


# ─────────────────────────────────────────────────────────────────────────────
# TestEditFlowFails
# ─────────────────────────────────────────────────────────────────────────────


class TestEditFlowFails:
    """Edited text fails validator → stays pending with text_history appended."""

    def test_invalid_edit_shows_validator_error(
        self, client, tmp_queue_root: Path
    ) -> None:
        draft = _make_draft()
        _write_draft_to_queue(draft, "pending", tmp_queue_root)

        client.get(f"/draft/{draft.draft_id}/edit")
        with client.session_transaction() as sess:
            csrf_token = sess.get("csrf_token", "")

        # Text with forbidden vocab (worldview)
        bad_text = "The model's worldview shapes its categorical structure output."
        rv = client.post(
            f"/draft/{draft.draft_id}/edit",
            data={"csrf_token": csrf_token, "text": bad_text, "action": "save"},
        )
        html = rv.data.decode("utf-8")
        assert "Edit did not pass validator" in html

    def test_invalid_edit_stays_pending(
        self, client, tmp_queue_root: Path
    ) -> None:
        draft = _make_draft()
        _write_draft_to_queue(draft, "pending", tmp_queue_root)

        client.get(f"/draft/{draft.draft_id}/edit")
        with client.session_transaction() as sess:
            csrf_token = sess.get("csrf_token", "")

        bad_text = "The model's worldview shapes its categorical structure."
        client.post(
            f"/draft/{draft.draft_id}/edit",
            data={"csrf_token": csrf_token, "text": bad_text, "action": "save"},
        )

        # Draft stays in pending
        assert (tmp_queue_root / "pending" / f"{draft.draft_id}.json").exists()

    def test_invalid_edit_appends_text_history(
        self, client, tmp_queue_root: Path
    ) -> None:
        original_text = "Original text (95% CI [0.70, 0.90])."
        draft = _make_draft(text=original_text)
        _write_draft_to_queue(draft, "pending", tmp_queue_root)

        client.get(f"/draft/{draft.draft_id}/edit")
        with client.session_transaction() as sess:
            csrf_token = sess.get("csrf_token", "")

        bad_text = "The model's worldview shapes everything."
        client.post(
            f"/draft/{draft.draft_id}/edit",
            data={"csrf_token": csrf_token, "text": bad_text, "action": "save"},
        )

        pending_path = tmp_queue_root / "pending" / f"{draft.draft_id}.json"
        saved = json.loads(pending_path.read_text(encoding="utf-8"))
        # original text should be in text_history
        assert original_text in saved.get("text_history", [])


# ─────────────────────────────────────────────────────────────────────────────
# TestPublishFlow
# ─────────────────────────────────────────────────────────────────────────────


class TestPublishFlow:
    """Publish confirm page has binding wording; POST invokes publisher."""

    def test_publish_confirm_has_binding_wording(
        self, client, tmp_queue_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Per CDA SME §5.9: exact wording for publish irreversibility."""
        monkeypatch.setenv("BLUESKY_HANDLE", "testhandle.bsky.social")
        draft = _make_draft(platform=Platform.BLUESKY)
        _write_draft_to_queue(draft, "approved", tmp_queue_root)
        rv = client.get(f"/draft/{draft.draft_id}/publish")
        assert rv.status_code == 200
        html = rv.data.decode("utf-8")
        # §5.9 binding wording verbatim
        assert "Once posted, deletion is best-effort" in html
        assert "timestamp and any platform-side cache may persist" in html
        assert "@testhandle.bsky.social" in html

    def test_publish_confirm_has_yes_publish_button(
        self, client, tmp_queue_root: Path
    ) -> None:
        draft = _make_draft(platform=Platform.BLUESKY)
        _write_draft_to_queue(draft, "approved", tmp_queue_root)
        rv = client.get(f"/draft/{draft.draft_id}/publish")
        html = rv.data.decode("utf-8")
        assert "Yes, publish to Bluesky" in html

    def test_publish_calls_publisher_and_redirects(
        self, client, tmp_queue_root: Path
    ) -> None:
        draft = _make_draft(platform=Platform.BLUESKY)
        _write_draft_to_queue(draft, "approved", tmp_queue_root)
        post_record = SocialPostRecord(
            draft_id=draft.draft_id,
            published_at=datetime.now(UTC),
            platform_post_id="at://did:plc:abc123/app.bsky.feed.post/rkey1",
            platform_post_url="https://bsky.app/profile/testhandle.bsky.social/post/rkey1",
            publish_status=PublishStatus.PUBLISHED,
        )

        client.get(f"/draft/{draft.draft_id}/publish")
        with client.session_transaction() as sess:
            csrf_token = sess.get("csrf_token", "")

        with patch(
            "cdb_social.admin_console.routes.publish", return_value=post_record
        ):
            post_rv = client.post(
                f"/draft/{draft.draft_id}/publish",
                data={"csrf_token": csrf_token},
                follow_redirects=False,
            )
        assert post_rv.status_code == 302

    def test_x_draft_shows_publisher_not_enabled(
        self, client, tmp_queue_root: Path
    ) -> None:
        """X draft shows 'Publishing not enabled' on publish GET."""
        trigger = _make_trigger()
        draft = _make_draft(
            draft_id="xdraftid1234abc",
            platform=Platform.X,
            trigger=trigger,
        )
        _write_draft_to_queue(draft, "approved", tmp_queue_root)
        rv = client.get(f"/draft/{draft.draft_id}/publish")
        html = rv.data.decode("utf-8")
        assert "not enabled" in html.lower() or "Publishing not enabled" in html

    def test_linkedin_draft_raises_publisher_not_enabled(
        self, client, tmp_queue_root: Path
    ) -> None:
        """LinkedIn draft POST raises PublisherNotEnabled and renders error."""
        trigger = _make_trigger()
        draft = _make_draft(
            draft_id="liraftid12345ab",
            platform=Platform.LINKEDIN,
            trigger=trigger,
        )
        _write_draft_to_queue(draft, "approved", tmp_queue_root)

        client.get(f"/draft/{draft.draft_id}/publish")
        with client.session_transaction() as sess:
            csrf_token = sess.get("csrf_token", "")

        with patch(
            "cdb_social.admin_console.routes.publish",
            side_effect=PublisherNotEnabled("LinkedIn not enabled"),
        ):
            rv = client.post(
                f"/draft/{draft.draft_id}/publish",
                data={"csrf_token": csrf_token},
            )
        html = rv.data.decode("utf-8")
        assert "not enabled" in html.lower()


# ─────────────────────────────────────────────────────────────────────────────
# TestCSRFProtection
# ─────────────────────────────────────────────────────────────────────────────


class TestCSRFProtection:
    """POST without CSRF token returns 403."""

    def test_approve_without_csrf_returns_403(
        self, client, tmp_queue_root: Path
    ) -> None:
        draft = _make_draft()
        _write_draft_to_queue(draft, "pending", tmp_queue_root)
        rv = client.post(f"/draft/{draft.draft_id}/approve", data={})
        assert rv.status_code == 403

    def test_reject_without_csrf_returns_403(
        self, client, tmp_queue_root: Path
    ) -> None:
        draft = _make_draft()
        _write_draft_to_queue(draft, "pending", tmp_queue_root)
        rv = client.post(
            f"/draft/{draft.draft_id}/reject",
            data={"reason": "other"},
        )
        assert rv.status_code == 403

    def test_publish_without_csrf_returns_403(
        self, client, tmp_queue_root: Path
    ) -> None:
        draft = _make_draft(platform=Platform.BLUESKY)
        _write_draft_to_queue(draft, "approved", tmp_queue_root)
        rv = client.post(f"/draft/{draft.draft_id}/publish", data={})
        assert rv.status_code == 403

    def test_draft_request_without_csrf_returns_403(
        self, client, tmp_state_dir: Path
    ) -> None:
        trigger = _make_trigger()
        _write_detected_triggers(tmp_state_dir, [trigger])
        rv = client.post(
            f"/triggers/{trigger.dedupe_key}/draft?platform=bluesky",
            data={},
        )
        assert rv.status_code == 403

    def test_wrong_csrf_token_returns_403(
        self, client, tmp_queue_root: Path
    ) -> None:
        draft = _make_draft()
        _write_draft_to_queue(draft, "pending", tmp_queue_root)
        rv = client.post(
            f"/draft/{draft.draft_id}/approve",
            data={"csrf_token": "wrongtoken"},
        )
        assert rv.status_code == 403


# ─────────────────────────────────────────────────────────────────────────────
# TestForbiddenVocabAbsent
# ─────────────────────────────────────────────────────────────────────────────


class TestForbiddenVocabAbsent:
    """Rendered HTML must not contain forbidden phrases from CDA SME §5.10."""

    FORBIDDEN_PHRASES = [
        "state of cultural alignment",
        "pairwise gap",
    ]
    # "worldview" is forbidden only in LSB methodology context (per CLAUDE.md §7).
    # "Confidence" is forbidden as a label for drafter_self_rating (§5.7).

    def _check_html(self, html: str) -> None:
        lower = html.lower()
        for phrase in self.FORBIDDEN_PHRASES:
            assert phrase.lower() not in lower, (
                f"Forbidden phrase {phrase!r} found in rendered HTML"
            )

    def test_index_no_forbidden_vocab(self, client) -> None:
        rv = client.get("/")
        self._check_html(rv.data.decode("utf-8"))

    def test_triggers_list_no_forbidden_vocab(
        self, client, tmp_state_dir: Path
    ) -> None:
        triggers = [
            _make_trigger(trigger_type=TriggerType.MONTHLY_ROUNDUP,
                         evidence={"month": "2026-05"}, dedupe_key="monthlyk1234567"),
            _make_trigger(trigger_type=TriggerType.DIVERGENCE, dedupe_key="divrgk12345678"),
            _make_trigger(trigger_type=TriggerType.DRIFT, evidence={
                "model_version_returned": "gpt-4-0125",
                "procrustes_distance": 0.18,
                "date_pair": ["2026-04-01", "2026-05-01"],
            }, dedupe_key="driftkey12345678"),
        ]
        _write_detected_triggers(tmp_state_dir, triggers)
        rv = client.get("/triggers")
        self._check_html(rv.data.decode("utf-8"))

    def test_queue_pending_no_forbidden_vocab(
        self, client, tmp_queue_root: Path
    ) -> None:
        draft = _make_draft()
        _write_draft_to_queue(draft, "pending", tmp_queue_root)
        rv = client.get("/queue/pending")
        self._check_html(rv.data.decode("utf-8"))

    def test_draft_view_no_forbidden_vocab(
        self, client, tmp_queue_root: Path
    ) -> None:
        draft = _make_draft()
        _write_draft_to_queue(draft, "pending", tmp_queue_root)
        rv = client.get(f"/draft/{draft.draft_id}")
        self._check_html(rv.data.decode("utf-8"))

    def test_draft_view_drafter_self_rating_label(
        self, client, tmp_queue_root: Path
    ) -> None:
        """Draft view must use 'Drafter self-rating', not 'Confidence' per §5.7."""
        draft = _make_draft()
        _write_draft_to_queue(draft, "pending", tmp_queue_root)
        rv = client.get(f"/draft/{draft.draft_id}")
        html = rv.data.decode("utf-8")
        assert "Drafter self-rating" in html
        # "Confidence" must not appear as a field label
        assert "Confidence:" not in html
        assert "Confidence score" not in html


# ─────────────────────────────────────────────────────────────────────────────
# TestBindingWordingPresent
# ─────────────────────────────────────────────────────────────────────────────


class TestBindingWordingPresent:
    """Trigger summaries contain CDA SME §5.7 binding wording."""

    def test_divergence_trigger_shows_max_pairwise_distance(
        self, client, tmp_state_dir: Path
    ) -> None:
        """DIVERGENCE trigger summary uses 'max pairwise distance' per T5 §5.7."""
        trigger = _make_trigger(
            trigger_type=TriggerType.DIVERGENCE,
            evidence={
                "model_pair": ["gpt-4", "claude-3"],
                "old_high": 0.72,
                "new_high": 0.85,
                "gap_delta": 0.13,
                "domain_slug": "family",
            },
            dedupe_key="divrgkey12345678",
        )
        _write_detected_triggers(tmp_state_dir, [trigger])
        rv = client.get("/triggers")
        html = rv.data.decode("utf-8")
        assert "max pairwise distance" in html

    def test_drift_trigger_shows_procrustes_distance(
        self, client, tmp_state_dir: Path
    ) -> None:
        """DRIFT trigger summary uses 'Procrustes distance' per T5 §5.7."""
        trigger = _make_trigger(
            trigger_type=TriggerType.DRIFT,
            evidence={
                "model_version_returned": "gpt-4-0125-preview",
                "procrustes_distance": 0.18,
                "date_pair": ["2026-04-01", "2026-05-01"],
            },
            dedupe_key="driftkey123456789",
        )
        _write_detected_triggers(tmp_state_dir, [trigger])
        rv = client.get("/triggers")
        html = rv.data.decode("utf-8")
        assert "Procrustes distance" in html

    def test_drift_trigger_shows_caveat(
        self, client, tmp_state_dir: Path
    ) -> None:
        """DRIFT trigger summary includes placeholder caveat per T5 §5.7."""
        trigger = _make_trigger(
            trigger_type=TriggerType.DRIFT,
            evidence={
                "model_version_returned": "gpt-4-0125-preview",
                "procrustes_distance": 0.18,
                "date_pair": ["2026-04-01", "2026-05-01"],
            },
            dedupe_key="driftkey1234abcde",
        )
        _write_detected_triggers(tmp_state_dir, [trigger])
        rv = client.get("/triggers")
        html = rv.data.decode("utf-8")
        assert "threshold 0.15 placeholder" in html
        assert "lockout engaged" in html

    def test_monthly_roundup_trigger_shows_binding_wording(
        self, client, tmp_state_dir: Path
    ) -> None:
        """MONTHLY_ROUNDUP uses 'Monthly cross-domain categorical-structure roundup'."""
        trigger = _make_trigger(
            trigger_type=TriggerType.MONTHLY_ROUNDUP,
            evidence={"month": "2026-05"},
            dedupe_key="monthlykey1234567",
        )
        _write_detected_triggers(tmp_state_dir, [trigger])
        rv = client.get("/triggers")
        html = rv.data.decode("utf-8")
        assert "Monthly cross-domain categorical-structure roundup" in html

    def test_framing_checks_keys_verbatim(
        self, client, tmp_queue_root: Path
    ) -> None:
        """Draft view shows framing_checks keys verbatim per §5.5."""
        draft = _make_draft()
        _write_draft_to_queue(draft, "pending", tmp_queue_root)
        rv = client.get(f"/draft/{draft.draft_id}")
        html = rv.data.decode("utf-8")
        assert "hypothesis_framing" in html
        assert "cognition_attribution" in html
        assert "bare_numeric_without_ci" in html
        assert "register_boundary" in html


# ─────────────────────────────────────────────────────────────────────────────
# TestLoadDomainResultForTrigger (T2 nested-path fix)
#
# _load_domain_result_for_trigger previously constructed a NESTED path:
#   data_dir / domain_slug / f"{analysis_version}.json"
# The publisher never writes that form; it writes flat versioned files:
#   data_dir / f"{slug}.v{version}.json"     (primary)
#   data_dir / f"{slug}.json"                (unversioned fallback)
# So the old code always fell through to _make_stub_domain_result, meaning
# every admin draft was based on stub data rather than real domain results.
#
# These tests call _load_domain_result_for_trigger directly (no Flask client,
# no drafter mocks) to confirm it now loads the real flat-published file.
# ─────────────────────────────────────────────────────────────────────────────


def _make_minimal_domain_result_json(domain_slug: str, analysis_version: str) -> str:
    """Return a minimal DomainResult JSON string for test fixtures."""
    from datetime import date  # noqa: PLC0415

    from cdb_core.schemas import BootstrapEllipse, DomainResult, FreeList, ModelRef  # noqa: PLC0415

    model_id = "fixture-routes-model"
    m = ModelRef(
        provider="anthropic",
        model_id=model_id,
        family="fixture",
        origin="us",
        open_weights=False,
        collection_method="anthropic_api",
        quantization=None,
        release_date=date(2026, 1, 1),
        version_label="1.0",
    )
    dr = DomainResult(
        domain_slug=domain_slug,
        analysis_version=analysis_version,
        models=[m],
        free_lists={
            model_id: FreeList(
                run_id="fixture_run_routes",
                model=m,
                domain_slug=domain_slug,
                items=["item-a", "item-b", "item-c"],
                raw_order=["item-a", "item-b", "item-c"],
            )
        },
        mds_coordinates={model_id: (0.1, 0.2)},
        mds_uncertainty={
            model_id: BootstrapEllipse(
                center=(0.1, 0.2),
                semi_major=0.12,
                semi_minor=0.06,
                rotation_rad=0.0,
                n_bootstrap=100,
            )
        },
        similarity_matrix=[[1.0]],
        similarity_ci=[[(0.9, 1.0)]],
        consensus_score=3.5,
        consensus_ci=(2.5, 4.5),
        groundings=[],
        selected_baseline_id=None,
        generated_lede="Routes fixture lede.",
        generated_at=datetime(2026, 5, 17, 12, 0, 0),
    )
    return dr.model_dump_json()


class TestLoadDomainResultForTrigger:
    """Unit tests for routes._load_domain_result_for_trigger — T2 flat-path fix.

    Anti-recurrence gate: the old code built ``data_dir / slug / version.json``
    (nested) which the publisher never writes.  These tests confirm that the
    function now loads real data from the flat publisher paths and returns a
    DomainResult with actual model content, not the stub's empty lists.
    """

    def test_loads_real_versioned_flat_file(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Primary path: {slug}.v{version}.json is loaded; result has real models.

        If the nested-path bug is re-introduced, the flat file will not be found,
        the function will fall back to the stub, and result.models == [] will fail.
        """
        from cdb_social.admin_console.routes import _load_domain_result_for_trigger  # noqa: PLC0415

        data_dir = tmp_path / "data"
        data_dir.mkdir()

        # Write manifest so analysis_version is derived correctly
        (data_dir / "manifest.json").write_text(
            json.dumps({
                "built_at": "2026-05-17T12:00:00Z",
                "domains": [
                    {
                        "slug": "family",
                        "analysis_version": "0.3",
                        "model_ids": ["fixture-routes-model"],
                    },
                ],
            }),
            encoding="utf-8",
        )

        # Write FLAT versioned file — the only form the publisher produces
        (data_dir / "family.v0.3.json").write_text(
            _make_minimal_domain_result_json("family", "0.3"),
            encoding="utf-8",
        )

        # Confirm old nested form does NOT exist (anti-recurrence context)
        assert not (data_dir / "family" / "0.3.json").exists()

        monkeypatch.setenv("LSB_SOCIAL_DATA_DIR", str(data_dir))

        trigger = _make_trigger(
            trigger_type=TriggerType.DIVERGENCE,
            domain_slug="family",
            dedupe_key="routest001routes01",
        )
        result = _load_domain_result_for_trigger(trigger)

        # Real file has one model; stub has models=[]
        assert len(result.models) == 1, (
            f"Expected 1 model from real domain file; got {len(result.models)}. "
            "If this fails, _load_domain_result_for_trigger is still using "
            "the old nested path and returning the stub."
        )
        assert result.domain_slug == "family"
        assert result.analysis_version == "0.3"
        assert result.models[0].model_id == "fixture-routes-model"

    def test_nested_path_not_loaded(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Old nested form data_dir/{slug}/{version}.json is NOT loaded — returns stub.

        Writing only the nested form (never produced by publisher) must result
        in stub (models=[]), confirming the loader ignores the nested path.
        """
        from cdb_social.admin_console.routes import _load_domain_result_for_trigger  # noqa: PLC0415

        data_dir = tmp_path / "data"
        data_dir.mkdir()

        (data_dir / "manifest.json").write_text(
            json.dumps({
                "built_at": "2026-05-17T12:00:00Z",
                "domains": [
                    {
                        "slug": "family",
                        "analysis_version": "0.3",
                        "model_ids": ["fixture-routes-model"],
                    },
                ],
            }),
            encoding="utf-8",
        )

        # Write ONLY nested form — should be invisible to the fixed loader
        nested = data_dir / "family"
        nested.mkdir()
        (nested / "0.3.json").write_text(
            _make_minimal_domain_result_json("family", "0.3"),
            encoding="utf-8",
        )

        monkeypatch.setenv("LSB_SOCIAL_DATA_DIR", str(data_dir))

        trigger = _make_trigger(
            trigger_type=TriggerType.DIVERGENCE,
            domain_slug="family",
            dedupe_key="routest002routes02",
        )
        result = _load_domain_result_for_trigger(trigger)

        # Stub has models=[] — confirms nested path ignored
        assert result.models == [], (
            "Expected stub (models=[]) when only nested form exists; "
            "if this fails, the loader is reading the nested path — "
            "the T2 flat-path fix may have been reverted."
        )

    def test_unversioned_fallback_returns_real_data(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Fallback: {slug}.json (no versioned form) still loads real data, not stub."""
        from cdb_social.admin_console.routes import _load_domain_result_for_trigger  # noqa: PLC0415

        data_dir = tmp_path / "data"
        data_dir.mkdir()

        (data_dir / "manifest.json").write_text(
            json.dumps({
                "built_at": "2026-05-17T12:00:00Z",
                "domains": [
                    {
                        "slug": "family",
                        "analysis_version": "0.3",
                        "model_ids": ["fixture-routes-model"],
                    },
                ],
            }),
            encoding="utf-8",
        )

        # Write ONLY unversioned alias — versioned absent
        (data_dir / "family.json").write_text(
            _make_minimal_domain_result_json("family", "0.3"),
            encoding="utf-8",
        )

        monkeypatch.setenv("LSB_SOCIAL_DATA_DIR", str(data_dir))

        trigger = _make_trigger(
            trigger_type=TriggerType.DIVERGENCE,
            domain_slug="family",
            dedupe_key="routest003routes03",
        )
        result = _load_domain_result_for_trigger(trigger)

        assert len(result.models) == 1, (
            "Expected 1 model from unversioned fallback file; "
            "got stub (models=[])."
        )
        assert result.models[0].model_id == "fixture-routes-model"

    def test_both_absent_returns_stub(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """When both flat files are absent, stub DomainResult is returned."""
        from cdb_social.admin_console.routes import _load_domain_result_for_trigger  # noqa: PLC0415

        data_dir = tmp_path / "data"
        data_dir.mkdir()

        (data_dir / "manifest.json").write_text(
            json.dumps({
                "built_at": "2026-05-17T12:00:00Z",
                "domains": [
                    {"slug": "family", "analysis_version": "0.3", "model_ids": []},
                ],
            }),
            encoding="utf-8",
        )
        # No domain file written — both versioned and unversioned absent

        monkeypatch.setenv("LSB_SOCIAL_DATA_DIR", str(data_dir))

        trigger = _make_trigger(
            trigger_type=TriggerType.DIVERGENCE,
            domain_slug="family",
            dedupe_key="routest004routes04",
        )
        result = _load_domain_result_for_trigger(trigger)

        # Stub: models=[], analysis_version="0.2"
        assert result.models == []
        assert result.domain_slug == "family"
