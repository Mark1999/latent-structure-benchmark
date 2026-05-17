"""Minimal SMTP email sender for the LSB daily detection digest.

Reads credentials from environment variables:
  LSB_SMTP_USERNAME   — Gmail account (e.g. your@gmail.com)
  LSB_SMTP_PASSWORD   — Gmail app password (16-char, no spaces)
  LSB_DIGEST_RECIPIENT — Recipient email address

Only plain-text bodies are sent.  No HTML.  Audit-readable in mail clients
and easy to reconstruct from logs.

No LLM imports here — this module is pure transport mechanics per
Phase 7 §11.1 binding B-1.

See docs/status/2026-05-17-phase7-architect-kickoff.md §11.5.
"""

from __future__ import annotations

import os
import smtplib
from dataclasses import dataclass, field
from email.message import EmailMessage


class EmailConfigError(Exception):
    """Raised when a required environment variable is missing or invalid."""


class EmailSendError(Exception):
    """Raised when the SMTP send operation fails.

    Wraps the underlying smtplib exception so callers do not need to import
    smtplib to catch delivery errors.
    """


@dataclass
class EmailConfig:
    """SMTP configuration for Gmail.

    All fields are required.  Use ``EmailConfig.from_env()`` to construct from
    the three ``LSB_*`` environment variables.
    """

    username: str
    password: str
    recipient: str
    smtp_host: str = field(default="smtp.gmail.com")
    smtp_port: int = field(default=465)  # SSL

    @classmethod
    def from_env(cls) -> EmailConfig:
        """Construct an EmailConfig from environment variables.

        Required env vars:
          LSB_SMTP_USERNAME    — Gmail sender address
          LSB_SMTP_PASSWORD    — Gmail app password
          LSB_DIGEST_RECIPIENT — Recipient address

        Raises:
            EmailConfigError: if any required variable is absent or empty.
        """
        missing: list[str] = []

        username = os.environ.get("LSB_SMTP_USERNAME", "").strip()
        if not username:
            missing.append("LSB_SMTP_USERNAME")

        password = os.environ.get("LSB_SMTP_PASSWORD", "").strip()
        if not password:
            missing.append("LSB_SMTP_PASSWORD")

        recipient = os.environ.get("LSB_DIGEST_RECIPIENT", "").strip()
        if not recipient:
            missing.append("LSB_DIGEST_RECIPIENT")

        if missing:
            raise EmailConfigError(
                f"Missing required environment variable(s): {', '.join(missing)}. "
                "Set them in .env (gitignored) before running the detect command. "
                "See .env.example for the placeholder format."
            )

        return cls(
            username=username,
            password=password,
            recipient=recipient,
        )


def send_digest(
    subject: str,
    body: str,
    config: EmailConfig | None = None,
) -> None:
    """Send a plain-text email digest via Gmail SMTP SSL.

    Args:
        subject: The email subject line.
        body:    The plain-text email body.
        config:  EmailConfig instance.  If None, constructed from environment
                 via ``EmailConfig.from_env()``.

    Raises:
        EmailConfigError: if config is None and env vars are missing.
        EmailSendError:   if the SMTP session or send operation fails.
    """
    if config is None:
        config = EmailConfig.from_env()

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = config.username
    msg["To"] = config.recipient
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL(config.smtp_host, config.smtp_port) as smtp:
            smtp.login(config.username, config.password)
            smtp.send_message(msg)
    except smtplib.SMTPException as exc:
        raise EmailSendError(
            f"SMTP error sending digest to {config.recipient!r}: {exc}"
        ) from exc
    except OSError as exc:
        raise EmailSendError(
            f"Network error connecting to {config.smtp_host}:{config.smtp_port}: {exc}"
        ) from exc
