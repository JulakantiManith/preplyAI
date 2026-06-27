"""Async SMTP email client for application-level transactional emails.

Provides a resilient interface for sending transactional emails (e.g.,
notifications, session summaries) via SMTP. Implements 1 retry with
exponential backoff and structured logging for monitoring.

NOTE: Supabase Auth handles its own emails (verification, OTP, password reset,
magic-link) independently. To ensure Supabase Auth uses the same custom SMTP
credentials, configure them via the Supabase Dashboard under:
  Authentication → SMTP Settings
Set the same SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, and
SMTP_SENDER_EMAIL values there. This email_client.py is for application-level
transactional emails beyond what Supabase Auth handles natively.

Requirements: 1.1, 1.4, 17.3
"""

import asyncio
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

import aiosmtplib

from app.config import get_settings

logger = logging.getLogger(__name__)

# Retry configuration
MAX_RETRIES = 1
BASE_BACKOFF_SECONDS = 2.0

# Connection timeout (seconds)
SMTP_TIMEOUT = 30.0


class EmailClientError(Exception):
    """Raised when email sending fails after all retries."""

    pass


class EmailClient:
    """Async SMTP client with retry logic and connection management.

    Implements:
    - 1 retry with exponential backoff on failure
    - Graceful degradation when SMTP is not configured
    - Structured logging of send success/failure for monitoring
    - TLS/STARTTLS support based on port configuration

    Usage:
        client = EmailClient()
        await client.send_email(
            to="user@example.com",
            subject="Welcome",
            html_body="<h1>Hello!</h1>",
        )
    """

    def __init__(self) -> None:
        """Initialize the email client with SMTP settings from config."""
        settings = get_settings()
        self._host = settings.smtp_host
        self._port = settings.smtp_port
        self._username = settings.smtp_username
        self._password = settings.smtp_password
        self._sender_email = settings.smtp_sender_email
        self._sender_name = settings.smtp_sender_name
        self._enabled = settings.get_smtp_enabled()

    @property
    def is_enabled(self) -> bool:
        """Check if SMTP is properly configured for sending emails."""
        return self._enabled

    def _build_message(
        self,
        to: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
    ) -> MIMEMultipart:
        """Build a MIME email message with HTML and optional plain-text parts.

        Args:
            to: Recipient email address.
            subject: Email subject line.
            html_body: HTML content for the email body.
            text_body: Optional plain-text fallback body.

        Returns:
            Constructed MIMEMultipart message ready to send.
        """
        message = MIMEMultipart("alternative")

        # Format sender with display name if available
        if self._sender_name:
            message["From"] = f"{self._sender_name} <{self._sender_email}>"
        else:
            message["From"] = self._sender_email

        message["To"] = to
        message["Subject"] = subject

        # Attach plain-text part first (lower priority in multipart/alternative)
        if text_body:
            message.attach(MIMEText(text_body, "plain", "utf-8"))

        # Attach HTML part (higher priority)
        message.attach(MIMEText(html_body, "html", "utf-8"))

        return message

    def _get_use_tls(self) -> bool:
        """Determine whether to use implicit TLS based on port.

        Port 465 uses implicit SSL/TLS. Other ports (587, 25) use STARTTLS.

        Returns:
            True if implicit TLS should be used (port 465).
        """
        return self._port == 465

    async def _send_single_attempt(self, message: MIMEMultipart, to: str) -> None:
        """Attempt a single SMTP send operation.

        Opens a connection, authenticates if credentials are provided,
        and sends the message.

        Args:
            message: The constructed MIME message.
            to: Recipient email address.

        Raises:
            aiosmtplib.SMTPException: On any SMTP-level error.
            asyncio.TimeoutError: If connection or send exceeds timeout.
            OSError: On network-level connection failures.
        """
        use_tls = self._get_use_tls()
        start_tls = not use_tls and self._port != 25

        smtp = aiosmtplib.SMTP(
            hostname=self._host,
            port=self._port,
            use_tls=use_tls,
            timeout=SMTP_TIMEOUT,
        )

        await smtp.connect()

        try:
            # Upgrade to TLS via STARTTLS for port 587
            if start_tls:
                await smtp.starttls()

            # Authenticate if credentials are provided
            if self._username and self._password:
                await smtp.login(self._username, self._password)

            await smtp.send_message(message)
        finally:
            try:
                await smtp.quit()
            except Exception:
                # Best-effort close; don't mask the original error
                pass

    async def send_email(
        self,
        to: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
    ) -> bool:
        """Send a transactional email with retry logic.

        If SMTP is not configured, logs a warning and returns False without
        raising an error. On transient failures, retries once with exponential
        backoff before raising EmailClientError.

        Args:
            to: Recipient email address.
            subject: Email subject line.
            html_body: HTML content for the email body.
            text_body: Optional plain-text fallback body.

        Returns:
            True if the email was sent successfully, False if SMTP is disabled.

        Raises:
            EmailClientError: If sending fails after all retry attempts.
        """
        if not self._enabled:
            logger.warning(
                "Email not sent — SMTP is not configured. "
                "Recipient=%s, Subject=%s",
                to,
                subject,
            )
            return False

        message = self._build_message(to, subject, html_body, text_body)
        last_error: Optional[Exception] = None

        for attempt in range(MAX_RETRIES + 1):
            try:
                await self._send_single_attempt(message, to)
                logger.info(
                    "Email sent successfully — to=%s, subject=%s",
                    to,
                    subject,
                )
                return True

            except (
                aiosmtplib.SMTPException,
                asyncio.TimeoutError,
                OSError,
            ) as e:
                last_error = e
                if attempt < MAX_RETRIES:
                    backoff = BASE_BACKOFF_SECONDS * (2**attempt)
                    logger.warning(
                        "Email send failed (attempt %d/%d), retrying in %.1fs: %s",
                        attempt + 1,
                        MAX_RETRIES + 1,
                        backoff,
                        str(e),
                    )
                    await asyncio.sleep(backoff)
                else:
                    logger.error(
                        "Email send failed after %d attempts — to=%s, subject=%s, error=%s",
                        MAX_RETRIES + 1,
                        to,
                        subject,
                        str(e),
                    )

        raise EmailClientError(
            f"Failed to send email to {to} after {MAX_RETRIES + 1} attempts: {last_error}"
        )


# Module-level singleton instance for convenient import
email_client = EmailClient()
