"""Health check routes for application monitoring.

Provides endpoints to verify connectivity with external services
(e.g., SMTP server) without performing destructive actions.

Requirements: 17.2, 17.3
"""

import asyncio
import logging

import aiosmtplib
from fastapi import APIRouter

from app.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["Health"])

# Timeout for SMTP connectivity test (seconds)
SMTP_CHECK_TIMEOUT = 10.0


@router.get("/email")
async def email_health_check():
    """Verify SMTP connectivity without sending an email.

    Performs an authenticated connection test to the configured SMTP server.
    Returns status indicating whether the application can reach and
    authenticate with the mail server.

    Returns:
        - status: "healthy" | "unhealthy" | "disabled"
        - smtp_host: configured host (when enabled)
        - smtp_port: configured port (when enabled)
        - connection: "authenticated" | "failed" (when enabled)
        - tls: whether TLS is used (when healthy)
        - error: error message (when unhealthy)
        - message: explanation (when disabled)
    """
    settings = get_settings()

    if not settings.get_smtp_enabled():
        return {
            "status": "disabled",
            "message": "SMTP is not configured",
        }

    host = settings.smtp_host
    port = settings.smtp_port
    username = settings.smtp_username
    password = settings.smtp_password
    use_tls = port == 465
    start_tls = not use_tls and port != 25

    try:
        smtp = aiosmtplib.SMTP(
            hostname=host,
            port=port,
            use_tls=use_tls,
            timeout=SMTP_CHECK_TIMEOUT,
        )

        await smtp.connect()

        try:
            # Upgrade to TLS via STARTTLS for port 587
            if start_tls:
                await smtp.starttls()

            # Authenticate if credentials are provided
            if username and password:
                await smtp.login(username, password)

            logger.info(
                "Email health check passed — host=%s, port=%d",
                host,
                port,
            )

            return {
                "status": "healthy",
                "smtp_host": host,
                "smtp_port": port,
                "connection": "authenticated",
                "tls": use_tls or start_tls,
            }
        finally:
            try:
                await smtp.quit()
            except Exception:
                pass

    except (
        aiosmtplib.SMTPException,
        asyncio.TimeoutError,
        OSError,
    ) as e:
        error_msg = str(e)
        logger.warning(
            "Email health check failed — host=%s, port=%d, error=%s",
            host,
            port,
            error_msg,
        )

        return {
            "status": "unhealthy",
            "smtp_host": host,
            "smtp_port": port,
            "connection": "failed",
            "error": error_msg,
        }
