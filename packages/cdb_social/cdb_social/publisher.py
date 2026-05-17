"""Social post publisher — Phase 7 T6.

Bluesky-live via the AT Protocol (atproto Python client).
X and LinkedIn raise PublisherNotEnabled per Mark's kickoff §10 ratification
(Bluesky-only live publishing in v1; X + LinkedIn ship as draft-only until
the v1 social pipeline proves itself and X paid API + LinkedIn partner
program decisions are revisited).

Credentials come exclusively from environment variables:
    BLUESKY_HANDLE        — e.g. yourhandle.bsky.social
    BLUESKY_APP_PASSWORD  — app password from bsky.app settings

See ARCHITECTURE.md §4.6 and the Phase 7 kickoff
docs/status/2026-05-17-phase7-architect-kickoff.md §3 T6.
"""

from __future__ import annotations

import logging
import os
from datetime import UTC, datetime
from typing import Any

from cdb_core.schemas import Platform, PublishStatus, SocialDraft, SocialPostRecord

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Exceptions
# ─────────────────────────────────────────────────────────────────────────────


class PublisherNotEnabled(Exception):
    """Raised when a draft is for a platform without live publishing in v1.

    X and LinkedIn are draft-only in Phase 7. The CLI moves these drafts to
    failed/ with error_message="platform not enabled in v1".
    """


class PublisherTransientError(Exception):
    """Raised for retryable failures (HTTP 5xx, rate-limit, network timeouts).

    The CLI leaves the draft in approved/ so the next cron run retries.
    A retry record is appended to out/social/state/publish_retries.jsonl.
    """


class PublisherTerminalError(Exception):
    """Raised for non-retryable failures (auth, malformed post, banned account).

    The CLI moves the draft to failed/ with the error message verbatim.
    """


# ─────────────────────────────────────────────────────────────────────────────
# AT URI → bsky.app URL helper
# ─────────────────────────────────────────────────────────────────────────────


def _atproto_uri_to_url(uri: str, handle: str) -> str:
    """Construct the bsky.app post URL from an AT URI and the posting handle.

    AT URI format: at://{did}/app.bsky.feed.post/{rkey}
    Resulting URL: https://bsky.app/profile/{handle}/post/{rkey}

    Args:
        uri:    AT URI returned by atproto client in response.uri.
        handle: The Bluesky handle used to post (e.g. "yourhandle.bsky.social").

    Returns:
        Full https://bsky.app/... URL.
    """
    # uri form: at://did:plc:xxx.../app.bsky.feed.post/rkey
    rkey = uri.split("/")[-1]
    return f"https://bsky.app/profile/{handle}/post/{rkey}"


# ─────────────────────────────────────────────────────────────────────────────
# Bluesky publisher
# ─────────────────────────────────────────────────────────────────────────────


def _publish_bluesky(
    draft: SocialDraft,
    *,
    atproto_client: Any | None = None,
) -> SocialPostRecord:
    """Publish a Bluesky draft via the AT Protocol.

    Args:
        draft:          The approved SocialDraft to publish.
        atproto_client: Injected client (real or mock). If None, constructs
                        a real atproto.Client and logs in with env credentials.

    Returns:
        SocialPostRecord with publish_status=PUBLISHED and platform URLs.

    Raises:
        PublisherTerminalError: on credential absence or authentication failure.
        PublisherTransientError: on transient HTTP errors or rate limits.
    """
    handle = os.environ.get("BLUESKY_HANDLE", "")
    app_password = os.environ.get("BLUESKY_APP_PASSWORD", "")

    if not handle or not app_password:
        raise PublisherTerminalError("credentials missing")

    try:
        if atproto_client is not None:
            client = atproto_client
        else:
            from atproto import Client  # noqa: PLC0415
            client = Client()

        client.login(handle, app_password)
        response = client.send_post(text=draft.text)

        # Extract URI from response
        if hasattr(response, "uri"):
            at_uri: str = response.uri
        elif isinstance(response, dict):
            at_uri = response.get("uri", "")
        else:
            at_uri = str(response)

        post_url = _atproto_uri_to_url(at_uri, handle)

        return SocialPostRecord(
            draft_id=draft.draft_id,
            published_at=datetime.now(UTC),
            platform_post_id=at_uri,
            platform_post_url=post_url,
            publish_status=PublishStatus.PUBLISHED,
            error_message=None,
        )

    except PublisherTerminalError:
        raise
    except PublisherTransientError:
        raise
    except Exception as exc:
        # Classify by status code when available.
        exc_str = str(exc)
        exc_type = type(exc).__name__

        # Detect transient signals: 5xx, 429, timeout, network errors
        transient_signals = (
            "503", "502", "500", "504", "429",
            "timeout", "timed out", "connection", "network",
            "rate limit", "rate_limit", "ratelimit",
        )
        terminal_signals = ("401", "403", "400", "unauthorized", "forbidden", "bad request")

        lower_msg = exc_str.lower()
        if any(sig in lower_msg or sig in exc_type.lower() for sig in transient_signals):
            raise PublisherTransientError(
                f"Transient error publishing to Bluesky: {exc_str}"
            ) from exc

        if any(sig in lower_msg or sig in exc_type.lower() for sig in terminal_signals):
            raise PublisherTerminalError(
                f"Terminal error publishing to Bluesky: {exc_str}"
            ) from exc

        # Unknown errors are classified as terminal — do not retry blindly.
        raise PublisherTerminalError(
            f"Unexpected error publishing to Bluesky ({exc_type}): {exc_str}"
        ) from exc


# ─────────────────────────────────────────────────────────────────────────────
# Public interface
# ─────────────────────────────────────────────────────────────────────────────


def publish(
    draft: SocialDraft,
    *,
    dry_run: bool = False,
    atproto_client: Any | None = None,
) -> SocialPostRecord:
    """Dispatch a draft to its platform's publisher.

    Platform dispatch:
        BLUESKY   — live publish via atproto client (this function's primary path).
        X         — raises PublisherNotEnabled (draft-only in v1).
        LINKEDIN  — raises PublisherNotEnabled (draft-only in v1).

    Args:
        draft:          The approved SocialDraft to publish.
        dry_run:        If True, skip the real API call and return a DRY_RUN
                        record with a synthetic platform_post_url. The atproto
                        client is never invoked.
        atproto_client: Optional injected atproto.Client (real or mock). Used
                        by tests to avoid real API calls. Ignored for non-
                        Bluesky platforms and when dry_run=True.

    Returns:
        SocialPostRecord with publish_status reflecting the outcome.

    Raises:
        PublisherNotEnabled:    draft.platform is X or LINKEDIN.
        PublisherTransientError: Bluesky returned a retryable error.
        PublisherTerminalError:  Bluesky returned a non-retryable error, or
                                 credentials are missing.
    """
    if draft.platform == Platform.X:
        raise PublisherNotEnabled(
            "X (Twitter) publishing is not enabled in Phase 7 v1. "
            "X is draft-only; post manually from out/social/queue/approved/."
        )

    if draft.platform == Platform.LINKEDIN:
        raise PublisherNotEnabled(
            "LinkedIn publishing is not enabled in Phase 7 v1. "
            "LinkedIn is draft-only; post manually from out/social/queue/approved/."
        )

    # Bluesky path
    if draft.platform == Platform.BLUESKY:
        if dry_run:
            handle = os.environ.get("BLUESKY_HANDLE", "dry-run.bsky.social")
            synthetic_url = (
                f"https://bsky.app/profile/{handle}/post/dry-run-{draft.draft_id}"
            )
            return SocialPostRecord(
                draft_id=draft.draft_id,
                published_at=datetime.now(UTC),
                platform_post_id=f"at://did:dry-run/app.bsky.feed.post/{draft.draft_id}",
                platform_post_url=synthetic_url,
                publish_status=PublishStatus.DRY_RUN,
                error_message=None,
            )

        return _publish_bluesky(draft, atproto_client=atproto_client)

    # Guard: exhaustive platform enum coverage (mypy unreachable)
    raise PublisherTerminalError(  # pragma: no cover
        f"Unknown platform: {draft.platform!r}"
    )
