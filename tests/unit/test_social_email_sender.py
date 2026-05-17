"""Unit tests for cdb_social/email_sender.py — Phase 7 T6a.

No real SMTP connections. smtplib.SMTP_SSL is mocked throughout.

Test classes:
  TestEmailConfigFromEnv    — valid env → config; missing vars → EmailConfigError
  TestSendDigestMocked      — verifies send_message called with correct headers/body
  TestSendDigestSMTPError   — smtplib exception wrapped in EmailSendError
"""

from __future__ import annotations

import smtplib
from unittest.mock import MagicMock, patch

import pytest
from cdb_social.email_sender import (
    EmailConfig,
    EmailConfigError,
    EmailSendError,
    send_digest,
)

# ─────────────────────────────────────────────────────────────────────────────
# TestEmailConfigFromEnv
# ─────────────────────────────────────────────────────────────────────────────


class TestEmailConfigFromEnv:
    def test_all_vars_set_returns_config(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("LSB_SMTP_USERNAME", "sender@example.com")
        monkeypatch.setenv("LSB_SMTP_PASSWORD", "app-pass-word-here")
        monkeypatch.setenv("LSB_DIGEST_RECIPIENT", "recipient@example.com")

        config = EmailConfig.from_env()

        assert config.username == "sender@example.com"
        assert config.password == "app-pass-word-here"
        assert config.recipient == "recipient@example.com"
        assert config.smtp_host == "smtp.gmail.com"
        assert config.smtp_port == 465

    def test_missing_username_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("LSB_SMTP_USERNAME", raising=False)
        monkeypatch.setenv("LSB_SMTP_PASSWORD", "app-pass-word-here")
        monkeypatch.setenv("LSB_DIGEST_RECIPIENT", "recipient@example.com")

        with pytest.raises(EmailConfigError) as exc_info:
            EmailConfig.from_env()

        assert "LSB_SMTP_USERNAME" in str(exc_info.value)

    def test_missing_password_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("LSB_SMTP_USERNAME", "sender@example.com")
        monkeypatch.delenv("LSB_SMTP_PASSWORD", raising=False)
        monkeypatch.setenv("LSB_DIGEST_RECIPIENT", "recipient@example.com")

        with pytest.raises(EmailConfigError) as exc_info:
            EmailConfig.from_env()

        assert "LSB_SMTP_PASSWORD" in str(exc_info.value)

    def test_missing_recipient_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("LSB_SMTP_USERNAME", "sender@example.com")
        monkeypatch.setenv("LSB_SMTP_PASSWORD", "app-pass-word-here")
        monkeypatch.delenv("LSB_DIGEST_RECIPIENT", raising=False)

        with pytest.raises(EmailConfigError) as exc_info:
            EmailConfig.from_env()

        assert "LSB_DIGEST_RECIPIENT" in str(exc_info.value)

    def test_all_vars_missing_raises_listing_all(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """All three missing — the error message names all three variables."""
        monkeypatch.delenv("LSB_SMTP_USERNAME", raising=False)
        monkeypatch.delenv("LSB_SMTP_PASSWORD", raising=False)
        monkeypatch.delenv("LSB_DIGEST_RECIPIENT", raising=False)

        with pytest.raises(EmailConfigError) as exc_info:
            EmailConfig.from_env()

        error_msg = str(exc_info.value)
        assert "LSB_SMTP_USERNAME" in error_msg
        assert "LSB_SMTP_PASSWORD" in error_msg
        assert "LSB_DIGEST_RECIPIENT" in error_msg

    def test_empty_string_username_raises(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Empty string is treated the same as absent."""
        monkeypatch.setenv("LSB_SMTP_USERNAME", "   ")
        monkeypatch.setenv("LSB_SMTP_PASSWORD", "app-pass")
        monkeypatch.setenv("LSB_DIGEST_RECIPIENT", "recip@example.com")

        with pytest.raises(EmailConfigError):
            EmailConfig.from_env()

    def test_custom_smtp_defaults_preserved(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Config built via from_env() uses Gmail defaults."""
        monkeypatch.setenv("LSB_SMTP_USERNAME", "u@example.com")
        monkeypatch.setenv("LSB_SMTP_PASSWORD", "pw")
        monkeypatch.setenv("LSB_DIGEST_RECIPIENT", "r@example.com")

        config = EmailConfig.from_env()
        assert config.smtp_host == "smtp.gmail.com"
        assert config.smtp_port == 465


# ─────────────────────────────────────────────────────────────────────────────
# TestSendDigestMocked
# ─────────────────────────────────────────────────────────────────────────────


class TestSendDigestMocked:
    """Patches smtplib.SMTP_SSL; verifies send_message is called with correct data."""

    _CONFIG = EmailConfig(
        username="sender@example.com",
        password="testpassword",
        recipient="recipient@example.com",
    )

    def _make_smtp_mock(self) -> tuple[MagicMock, MagicMock]:
        """Return (smtp_class_mock, smtp_instance_mock).

        smtp_class_mock is used in `patch("smtplib.SMTP_SSL", smtp_class_mock)`.
        smtp_instance_mock is the context-manager __enter__ return value that
        send_digest interacts with (calling .login() and .send_message()).
        """
        smtp_instance = MagicMock()
        smtp_class = MagicMock()
        smtp_class.return_value.__enter__ = MagicMock(return_value=smtp_instance)
        smtp_class.return_value.__exit__ = MagicMock(return_value=False)
        return smtp_class, smtp_instance

    def test_send_message_called_once(self) -> None:
        smtp_class, smtp_instance = self._make_smtp_mock()
        with patch("smtplib.SMTP_SSL", smtp_class):
            send_digest("Test Subject", "Test body.", config=self._CONFIG)
        smtp_instance.send_message.assert_called_once()

    def test_send_message_has_correct_subject(self) -> None:
        smtp_class, smtp_instance = self._make_smtp_mock()
        with patch("smtplib.SMTP_SSL", smtp_class):
            send_digest("My Subject Line", "Body text.", config=self._CONFIG)

        call_args = smtp_instance.send_message.call_args
        msg = call_args[0][0]
        assert msg["Subject"] == "My Subject Line"

    def test_send_message_has_correct_from(self) -> None:
        smtp_class, smtp_instance = self._make_smtp_mock()
        with patch("smtplib.SMTP_SSL", smtp_class):
            send_digest("Subject", "Body.", config=self._CONFIG)

        call_args = smtp_instance.send_message.call_args
        msg = call_args[0][0]
        assert msg["From"] == "sender@example.com"

    def test_send_message_has_correct_to(self) -> None:
        smtp_class, smtp_instance = self._make_smtp_mock()
        with patch("smtplib.SMTP_SSL", smtp_class):
            send_digest("Subject", "Body.", config=self._CONFIG)

        call_args = smtp_instance.send_message.call_args
        msg = call_args[0][0]
        assert msg["To"] == "recipient@example.com"

    def test_login_called_with_credentials(self) -> None:
        smtp_class, smtp_instance = self._make_smtp_mock()
        with patch("smtplib.SMTP_SSL", smtp_class):
            send_digest("Subject", "Body.", config=self._CONFIG)

        smtp_instance.login.assert_called_once_with(
            "sender@example.com", "testpassword"
        )

    def test_smtp_ssl_uses_configured_host_and_port(self) -> None:
        config = EmailConfig(
            username="u@example.com",
            password="pw",
            recipient="r@example.com",
            smtp_host="smtp.custom.com",
            smtp_port=587,
        )
        smtp_class, _ = self._make_smtp_mock()
        with patch("smtplib.SMTP_SSL", smtp_class):
            send_digest("Subject", "Body.", config=config)

        smtp_class.assert_called_once_with("smtp.custom.com", 587)

    def test_body_content_passed_to_message(self) -> None:
        """The body string is included in the EmailMessage payload."""
        from email.message import EmailMessage

        captured_msgs: list[EmailMessage] = []

        def capture_send(msg: EmailMessage) -> None:
            captured_msgs.append(msg)

        smtp_class, smtp_instance = self._make_smtp_mock()
        smtp_instance.send_message.side_effect = capture_send

        with patch("smtplib.SMTP_SSL", smtp_class):
            send_digest("Subject", "Hello, this is the digest body.", config=self._CONFIG)

        assert len(captured_msgs) == 1
        # The body is in the message payload
        payload = captured_msgs[0].get_payload()
        assert "Hello, this is the digest body." in payload


# ─────────────────────────────────────────────────────────────────────────────
# TestSendDigestSMTPError
# ─────────────────────────────────────────────────────────────────────────────


class TestSendDigestSMTPError:
    """smtplib exceptions are wrapped in EmailSendError."""

    _CONFIG = EmailConfig(
        username="sender@example.com",
        password="testpassword",
        recipient="recipient@example.com",
    )

    def _make_smtp_mock(self) -> tuple[MagicMock, MagicMock]:
        smtp_instance = MagicMock()
        smtp_class = MagicMock()
        smtp_class.return_value.__enter__ = MagicMock(return_value=smtp_instance)
        smtp_class.return_value.__exit__ = MagicMock(return_value=False)
        return smtp_class, smtp_instance

    def test_smtp_exception_wrapped_in_email_send_error(self) -> None:
        with patch("smtplib.SMTP_SSL") as mock_ssl_class:
            mock_ssl_class.side_effect = smtplib.SMTPException("Connection refused")
            with pytest.raises(EmailSendError) as exc_info:
                send_digest("Subject", "Body.", config=self._CONFIG)
        assert "Connection refused" in str(exc_info.value)

    def test_smtp_auth_error_wrapped(self) -> None:
        smtp_class, smtp_instance = self._make_smtp_mock()
        smtp_instance.login.side_effect = smtplib.SMTPAuthenticationError(535, b"Auth failed")
        with patch("smtplib.SMTP_SSL", smtp_class), pytest.raises(EmailSendError):
            send_digest("Subject", "Body.", config=self._CONFIG)

    def test_os_error_wrapped(self) -> None:
        """Network-level OSError is also wrapped in EmailSendError."""
        with patch("smtplib.SMTP_SSL") as mock_ssl_class:
            mock_ssl_class.side_effect = OSError("Network unreachable")
            with pytest.raises(EmailSendError) as exc_info:
                send_digest("Subject", "Body.", config=self._CONFIG)
        assert "Network unreachable" in str(exc_info.value)

    def test_send_message_error_wrapped(self) -> None:
        """SMTPException raised inside send_message is wrapped."""
        smtp_class, smtp_instance = self._make_smtp_mock()
        smtp_instance.send_message.side_effect = smtplib.SMTPException("Send failed")
        with patch("smtplib.SMTP_SSL", smtp_class), pytest.raises(EmailSendError) as exc_info:
            send_digest("Subject", "Body.", config=self._CONFIG)
        assert "Send failed" in str(exc_info.value)
