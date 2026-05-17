"""Unit tests for cdb_social/publisher.py — Phase 7 T6.

No real Bluesky API calls in this module. The atproto.Client is monkeypatched
to a mock object whose login() and send_post() methods are scripted.

Test classes:
  TestPublisherPlatformDispatch — dispatch by platform enum value
  TestPublisherCredentials      — missing env var raises PublisherTerminalError
  TestPublisherDryRun           — dry_run path; no real API call
  TestPublisherSuccess          — returns PUBLISHED record with AT URI + bsky URL
  TestPublisherTransientError   — 5xx/timeout → PublisherTransientError
  TestPublisherTerminalError    — 401/400 → PublisherTerminalError
"""

from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from cdb_core.schemas import Platform, PublishStatus, SocialDraft, SocialTrigger, TriggerType
from cdb_social.publisher import (
    PublisherNotEnabled,
    PublisherTerminalError,
    PublisherTransientError,
    _atproto_uri_to_url,
    publish,
)

# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────


def _make_trigger(
    trigger_type: TriggerType = TriggerType.NEW_MODEL,
    domain_slug: str | None = "family",
    model_id: str | None = "test-model",
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
    platform: Platform = Platform.BLUESKY,
    draft_id: str = "testdraftid1234",
    text: str = "Test Bluesky post about corpus lens patterns.",
) -> SocialDraft:
    return SocialDraft(
        draft_id=draft_id,
        trigger=_make_trigger(),
        platform=platform,
        text=text,
        suggested_posting_time=datetime(2026, 5, 19, 14, 0, 0, tzinfo=UTC),
        drafter_self_rating=0.5,
        methodology_url="https://cogstructurelab.com/family",
        dashboard_url="https://cogstructurelab.com/family",
        framing_check_passed=True,
        framing_checks={
            "hypothesis_framing": True,
            "cognition_attribution": True,
            "bare_numeric_without_ci": True,
            "register_boundary": True,
        },
        drafter_version="bluesky-v1",
        prompt_version="v1",
        created_at=datetime(2026, 5, 17, 10, 0, 0, tzinfo=UTC),
    )


def _make_mock_atproto_client(
    uri: str = "at://did:plc:abc123/app.bsky.feed.post/3jwvhsa5ocp2k",
    login_raises: Exception | None = None,
    send_post_raises: Exception | None = None,
) -> MagicMock:
    """Return a mock atproto.Client whose methods are scripted."""
    client = MagicMock()

    if login_raises is not None:
        client.login.side_effect = login_raises
    else:
        client.login.return_value = None

    if send_post_raises is not None:
        client.send_post.side_effect = send_post_raises
    else:
        # response.uri is the AT URI
        response = SimpleNamespace(uri=uri, cid="bafyxxx")
        client.send_post.return_value = response

    return client


@pytest.fixture(autouse=True)
def bluesky_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set Bluesky env vars for all tests. Individual tests may override."""
    monkeypatch.setenv("BLUESKY_HANDLE", "testhandle.bsky.social")
    monkeypatch.setenv("BLUESKY_APP_PASSWORD", "test-app-password-xxxx")


# ─────────────────────────────────────────────────────────────────────────────
# Helper tests
# ─────────────────────────────────────────────────────────────────────────────


class TestAtprotoUriToUrl:
    """Unit tests for the URI → URL converter."""

    def test_canonical_uri_format(self) -> None:
        uri = "at://did:plc:abc123def456/app.bsky.feed.post/3jwvhsa5ocp2k"
        url = _atproto_uri_to_url(uri, "myhandle.bsky.social")
        assert url == "https://bsky.app/profile/myhandle.bsky.social/post/3jwvhsa5ocp2k"

    def test_rkey_extraction(self) -> None:
        uri = "at://did:plc:xyz789/app.bsky.feed.post/my-rkey-value"
        url = _atproto_uri_to_url(uri, "handle.bsky.social")
        assert url.endswith("/post/my-rkey-value")
        assert "handle.bsky.social" in url


# ─────────────────────────────────────────────────────────────────────────────
# TestPublisherPlatformDispatch
# ─────────────────────────────────────────────────────────────────────────────


class TestPublisherPlatformDispatch:
    """Bluesky drafts go through the atproto path; X and LinkedIn raise PublisherNotEnabled."""

    def test_bluesky_draft_goes_through_atproto(self) -> None:
        """A BLUESKY draft returns a PUBLISHED record via the mock client."""
        draft = _make_draft(Platform.BLUESKY)
        mock_client = _make_mock_atproto_client()
        record = publish(draft, atproto_client=mock_client)

        assert record.publish_status == PublishStatus.PUBLISHED
        mock_client.login.assert_called_once()
        mock_client.send_post.assert_called_once_with(text=draft.text)

    def test_x_draft_raises_not_enabled(self) -> None:
        """An X draft raises PublisherNotEnabled."""
        draft = _make_draft(Platform.X)
        with pytest.raises(PublisherNotEnabled):
            publish(draft)

    def test_linkedin_draft_raises_not_enabled(self) -> None:
        """A LinkedIn draft raises PublisherNotEnabled."""
        draft = _make_draft(Platform.LINKEDIN)
        with pytest.raises(PublisherNotEnabled):
            publish(draft)

    def test_x_not_enabled_message_is_informative(self) -> None:
        """The PublisherNotEnabled message mentions 'draft-only'."""
        draft = _make_draft(Platform.X)
        with pytest.raises(PublisherNotEnabled, match="draft-only"):
            publish(draft)

    def test_linkedin_not_enabled_message_is_informative(self) -> None:
        """The PublisherNotEnabled message mentions 'draft-only'."""
        draft = _make_draft(Platform.LINKEDIN)
        with pytest.raises(PublisherNotEnabled, match="draft-only"):
            publish(draft)


# ─────────────────────────────────────────────────────────────────────────────
# TestPublisherCredentials
# ─────────────────────────────────────────────────────────────────────────────


class TestPublisherCredentials:
    """Missing credentials raise PublisherTerminalError."""

    def test_missing_handle_raises_terminal(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Missing BLUESKY_HANDLE raises PublisherTerminalError('credentials missing')."""
        monkeypatch.delenv("BLUESKY_HANDLE", raising=False)
        draft = _make_draft(Platform.BLUESKY)
        with pytest.raises(PublisherTerminalError, match="credentials missing"):
            publish(draft)

    def test_missing_password_raises_terminal(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Missing BLUESKY_APP_PASSWORD raises PublisherTerminalError('credentials missing')."""
        monkeypatch.delenv("BLUESKY_APP_PASSWORD", raising=False)
        draft = _make_draft(Platform.BLUESKY)
        with pytest.raises(PublisherTerminalError, match="credentials missing"):
            publish(draft)

    def test_empty_handle_raises_terminal(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Empty string BLUESKY_HANDLE raises PublisherTerminalError."""
        monkeypatch.setenv("BLUESKY_HANDLE", "")
        draft = _make_draft(Platform.BLUESKY)
        with pytest.raises(PublisherTerminalError, match="credentials missing"):
            publish(draft)

    def test_empty_password_raises_terminal(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Empty string BLUESKY_APP_PASSWORD raises PublisherTerminalError."""
        monkeypatch.setenv("BLUESKY_APP_PASSWORD", "")
        draft = _make_draft(Platform.BLUESKY)
        with pytest.raises(PublisherTerminalError, match="credentials missing"):
            publish(draft)

    def test_mock_client_not_called_on_missing_creds(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """When credentials are missing, the mock client is never invoked."""
        monkeypatch.delenv("BLUESKY_HANDLE", raising=False)
        draft = _make_draft(Platform.BLUESKY)
        mock_client = _make_mock_atproto_client()
        with pytest.raises(PublisherTerminalError):
            publish(draft, atproto_client=mock_client)
        mock_client.login.assert_not_called()
        mock_client.send_post.assert_not_called()


# ─────────────────────────────────────────────────────────────────────────────
# TestPublisherDryRun
# ─────────────────────────────────────────────────────────────────────────────


class TestPublisherDryRun:
    """dry_run=True path returns DRY_RUN record without calling the real API."""

    def test_dry_run_returns_dry_run_status(self) -> None:
        """dry_run=True returns a record with publish_status=DRY_RUN."""
        draft = _make_draft(Platform.BLUESKY)
        mock_client = _make_mock_atproto_client()
        record = publish(draft, dry_run=True, atproto_client=mock_client)

        assert record.publish_status == PublishStatus.DRY_RUN

    def test_dry_run_mock_client_never_invoked(self) -> None:
        """The mock client is never called in dry-run mode."""
        draft = _make_draft(Platform.BLUESKY)
        mock_client = _make_mock_atproto_client()
        publish(draft, dry_run=True, atproto_client=mock_client)

        mock_client.login.assert_not_called()
        mock_client.send_post.assert_not_called()

    def test_dry_run_has_synthetic_url(self) -> None:
        """dry_run record has a synthetic platform_post_url containing the draft_id."""
        draft = _make_draft(Platform.BLUESKY, draft_id="dryruntest1234")
        record = publish(draft, dry_run=True)

        assert record.platform_post_url is not None
        assert "dryruntest1234" in record.platform_post_url
        assert "bsky.app" in record.platform_post_url

    def test_dry_run_sets_draft_id(self) -> None:
        """dry_run record carries the same draft_id as the input draft."""
        draft = _make_draft(Platform.BLUESKY, draft_id="draftid99887766")
        record = publish(draft, dry_run=True)

        assert record.draft_id == "draftid99887766"

    def test_dry_run_x_still_raises_not_enabled(self) -> None:
        """dry_run has no effect on X — still raises PublisherNotEnabled."""
        draft = _make_draft(Platform.X)
        with pytest.raises(PublisherNotEnabled):
            publish(draft, dry_run=True)


# ─────────────────────────────────────────────────────────────────────────────
# TestPublisherSuccess
# ─────────────────────────────────────────────────────────────────────────────


class TestPublisherSuccess:
    """Successful publish returns SocialPostRecord with PUBLISHED status and AT URI."""

    AT_URI = "at://did:plc:abc123def456ghi789jkl012/app.bsky.feed.post/3jwvhsa5ocp2k"

    def test_publish_status_is_published(self) -> None:
        """Successful publish sets publish_status=PUBLISHED."""
        draft = _make_draft(Platform.BLUESKY)
        mock_client = _make_mock_atproto_client(uri=self.AT_URI)
        record = publish(draft, atproto_client=mock_client)

        assert record.publish_status == PublishStatus.PUBLISHED

    def test_platform_post_id_is_at_uri(self) -> None:
        """platform_post_id is set to the AT URI."""
        draft = _make_draft(Platform.BLUESKY)
        mock_client = _make_mock_atproto_client(uri=self.AT_URI)
        record = publish(draft, atproto_client=mock_client)

        assert record.platform_post_id == self.AT_URI

    def test_platform_post_url_is_bsky_app_url(self) -> None:
        """platform_post_url is a https://bsky.app/... URL."""
        draft = _make_draft(Platform.BLUESKY)
        mock_client = _make_mock_atproto_client(uri=self.AT_URI)
        record = publish(draft, atproto_client=mock_client)

        assert record.platform_post_url is not None
        assert record.platform_post_url.startswith("https://bsky.app/profile/")
        assert "/post/" in record.platform_post_url
        assert "3jwvhsa5ocp2k" in record.platform_post_url

    def test_platform_post_url_contains_handle(self) -> None:
        """platform_post_url contains the handle from env."""
        draft = _make_draft(Platform.BLUESKY)
        mock_client = _make_mock_atproto_client(uri=self.AT_URI)
        record = publish(draft, atproto_client=mock_client)

        assert "testhandle.bsky.social" in (record.platform_post_url or "")

    def test_draft_id_preserved(self) -> None:
        """The returned record carries the same draft_id."""
        draft = _make_draft(Platform.BLUESKY, draft_id="successdraftid1")
        mock_client = _make_mock_atproto_client(uri=self.AT_URI)
        record = publish(draft, atproto_client=mock_client)

        assert record.draft_id == "successdraftid1"

    def test_published_at_is_set(self) -> None:
        """published_at is a recent UTC datetime."""
        draft = _make_draft(Platform.BLUESKY)
        mock_client = _make_mock_atproto_client(uri=self.AT_URI)
        before = datetime.now(UTC)
        record = publish(draft, atproto_client=mock_client)
        after = datetime.now(UTC)

        assert before <= record.published_at <= after

    def test_login_called_with_credentials(self) -> None:
        """client.login() is called with the handle and password from env."""
        draft = _make_draft(Platform.BLUESKY)
        mock_client = _make_mock_atproto_client(uri=self.AT_URI)
        publish(draft, atproto_client=mock_client)

        mock_client.login.assert_called_once_with(
            "testhandle.bsky.social", "test-app-password-xxxx"
        )

    def test_send_post_called_with_draft_text(self) -> None:
        """client.send_post() is called with text=draft.text."""
        draft = _make_draft(Platform.BLUESKY, text="My post about corpus lens patterns.")
        mock_client = _make_mock_atproto_client(uri=self.AT_URI)
        publish(draft, atproto_client=mock_client)

        mock_client.send_post.assert_called_once_with(text="My post about corpus lens patterns.")

    def test_no_error_message_on_success(self) -> None:
        """error_message is None on successful publish."""
        draft = _make_draft(Platform.BLUESKY)
        mock_client = _make_mock_atproto_client(uri=self.AT_URI)
        record = publish(draft, atproto_client=mock_client)

        assert record.error_message is None


# ─────────────────────────────────────────────────────────────────────────────
# TestPublisherTransientError
# ─────────────────────────────────────────────────────────────────────────────


class TestPublisherTransientError:
    """Transient errors (5xx, timeout) raise PublisherTransientError."""

    def test_503_raises_transient(self) -> None:
        """An exception containing '503' is classified as transient."""
        draft = _make_draft(Platform.BLUESKY)
        mock_client = _make_mock_atproto_client(
            send_post_raises=Exception("HTTP 503 Service Unavailable")
        )
        with pytest.raises(PublisherTransientError):
            publish(draft, atproto_client=mock_client)

    def test_502_raises_transient(self) -> None:
        """An exception containing '502' is classified as transient."""
        draft = _make_draft(Platform.BLUESKY)
        mock_client = _make_mock_atproto_client(
            send_post_raises=Exception("502 Bad Gateway")
        )
        with pytest.raises(PublisherTransientError):
            publish(draft, atproto_client=mock_client)

    def test_429_raises_transient(self) -> None:
        """A rate-limit exception (429) is classified as transient."""
        draft = _make_draft(Platform.BLUESKY)
        mock_client = _make_mock_atproto_client(
            send_post_raises=Exception("429 rate limit exceeded")
        )
        with pytest.raises(PublisherTransientError):
            publish(draft, atproto_client=mock_client)

    def test_timeout_raises_transient(self) -> None:
        """A timeout exception is classified as transient."""
        draft = _make_draft(Platform.BLUESKY)
        mock_client = _make_mock_atproto_client(
            send_post_raises=TimeoutError("Connection timed out")
        )
        with pytest.raises(PublisherTransientError):
            publish(draft, atproto_client=mock_client)

    def test_network_error_raises_transient(self) -> None:
        """A network-related exception is classified as transient."""

        draft = _make_draft(Platform.BLUESKY)
        mock_client = _make_mock_atproto_client(
            send_post_raises=ConnectionError("network connection error")
        )
        with pytest.raises(PublisherTransientError):
            publish(draft, atproto_client=mock_client)

    def test_rate_limit_keyword_raises_transient(self) -> None:
        """An exception mentioning 'rate limit' is classified as transient."""
        draft = _make_draft(Platform.BLUESKY)
        mock_client = _make_mock_atproto_client(
            send_post_raises=Exception("rate limit reached")
        )
        with pytest.raises(PublisherTransientError):
            publish(draft, atproto_client=mock_client)


# ─────────────────────────────────────────────────────────────────────────────
# TestPublisherTerminalError
# ─────────────────────────────────────────────────────────────────────────────


class TestPublisherTerminalError:
    """Terminal errors (401, 400) raise PublisherTerminalError."""

    def test_401_raises_terminal(self) -> None:
        """An exception containing '401' (auth failure) is classified as terminal."""
        draft = _make_draft(Platform.BLUESKY)
        mock_client = _make_mock_atproto_client(
            send_post_raises=Exception("HTTP 401 Unauthorized")
        )
        with pytest.raises(PublisherTerminalError):
            publish(draft, atproto_client=mock_client)

    def test_401_on_login_raises_terminal(self) -> None:
        """A 401 during login is classified as terminal."""
        draft = _make_draft(Platform.BLUESKY)
        mock_client = _make_mock_atproto_client(
            login_raises=Exception("401 Invalid identifier or password")
        )
        with pytest.raises(PublisherTerminalError):
            publish(draft, atproto_client=mock_client)

    def test_403_raises_terminal(self) -> None:
        """An exception containing '403' (forbidden) is classified as terminal."""
        draft = _make_draft(Platform.BLUESKY)
        mock_client = _make_mock_atproto_client(
            send_post_raises=Exception("403 Forbidden")
        )
        with pytest.raises(PublisherTerminalError):
            publish(draft, atproto_client=mock_client)

    def test_400_raises_terminal(self) -> None:
        """An exception containing '400' (bad request) is classified as terminal."""
        draft = _make_draft(Platform.BLUESKY)
        mock_client = _make_mock_atproto_client(
            send_post_raises=Exception("400 Bad Request — post text too long")
        )
        with pytest.raises(PublisherTerminalError):
            publish(draft, atproto_client=mock_client)

    def test_unknown_exception_raises_terminal(self) -> None:
        """An unknown exception is classified as terminal (do not retry blindly)."""
        draft = _make_draft(Platform.BLUESKY)
        mock_client = _make_mock_atproto_client(
            send_post_raises=RuntimeError("Something completely unexpected")
        )
        with pytest.raises(PublisherTerminalError):
            publish(draft, atproto_client=mock_client)

    def test_unauthorized_keyword_raises_terminal(self) -> None:
        """An exception mentioning 'unauthorized' is classified as terminal."""
        draft = _make_draft(Platform.BLUESKY)
        mock_client = _make_mock_atproto_client(
            send_post_raises=Exception("unauthorized request")
        )
        with pytest.raises(PublisherTerminalError):
            publish(draft, atproto_client=mock_client)

    def test_terminal_error_message_is_verbatim(self) -> None:
        """The PublisherTerminalError message contains the original exception text."""
        draft = _make_draft(Platform.BLUESKY)
        mock_client = _make_mock_atproto_client(
            send_post_raises=Exception("401 Invalid credentials from test suite")
        )
        with pytest.raises(PublisherTerminalError, match="401"):
            publish(draft, atproto_client=mock_client)
