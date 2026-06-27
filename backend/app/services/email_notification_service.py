"""Email notification service for session completion notifications.

Sends branded email summaries after interview/presentation sessions are completed.
Implements fire-and-forget pattern — errors are logged but never raised to callers.

Requirements: 10.1, 16.1
"""

import logging
from pathlib import Path
from typing import Optional

from app.config import get_settings
from app.integrations.email_client import email_client

logger = logging.getLogger(__name__)

# Path to email templates directory
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates" / "emails"


def _get_score_color(score: Optional[float]) -> str:
    """Return a hex color based on the score value.

    Green for good (>=70), amber for moderate (>=50), red for low (<50).
    """
    if score is None:
        return "#6b7280"  # gray
    if score >= 70:
        return "#16a34a"  # green
    if score >= 50:
        return "#d97706"  # amber
    return "#dc2626"  # red


def _load_template() -> str:
    """Load the session complete email HTML template.

    Returns:
        HTML template string with placeholders.

    Raises:
        FileNotFoundError: If template file is missing.
    """
    template_path = TEMPLATES_DIR / "session_complete_email.html"
    return template_path.read_text(encoding="utf-8")


def _render_template(session_summary: dict) -> str:
    """Render the session complete email template with session data.

    Args:
        session_summary: Dict containing session_type, completed_at,
            overall_score, strengths, weaknesses, session_id.

    Returns:
        Rendered HTML string.
    """
    settings = get_settings()
    frontend_url = settings.get_resolved_frontend_url()

    template = _load_template()

    # Extract data with safe defaults
    session_type = session_summary.get("session_type", "Interview")
    session_date = session_summary.get("completed_at", "")
    overall_score = session_summary.get("overall_score")
    strengths = session_summary.get("strengths", [])
    weaknesses = session_summary.get("weaknesses", [])
    session_id = session_summary.get("session_id", "")

    # Format display values
    score_display = f"{int(overall_score)}" if overall_score is not None else "N/A"
    score_color = _get_score_color(overall_score)
    strength_1 = strengths[0] if len(strengths) > 0 else "Keep practicing!"
    strength_2 = strengths[1] if len(strengths) > 1 else ""
    improvement_area = weaknesses[0] if len(weaknesses) > 0 else "No specific areas flagged"
    report_url = f"{frontend_url}/history/{session_id}"

    # Format session date for display
    if session_date:
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(session_date.replace("Z", "+00:00"))
            session_date_display = dt.strftime("%B %d, %Y")
        except (ValueError, TypeError):
            session_date_display = session_date
    else:
        session_date_display = "Today"

    # Replace placeholders
    html = template
    html = html.replace("{{ session_type }}", session_type)
    html = html.replace("{{ session_date }}", session_date_display)
    html = html.replace("{{ overall_score }}", score_display)
    html = html.replace("{{ score_color }}", score_color)
    html = html.replace("{{ strength_1 }}", strength_1)
    html = html.replace("{{ strength_2 }}", strength_2)
    html = html.replace("{{ improvement_area }}", improvement_area)
    html = html.replace("{{ report_url }}", report_url)

    return html


async def send_session_complete_notification(
    user_email: str, session_summary: dict
) -> None:
    """Send a session completion notification email.

    This function is designed for fire-and-forget usage via asyncio.create_task().
    All exceptions are caught and logged — never raised.

    Args:
        user_email: The recipient's email address.
        session_summary: Dict containing:
            - session_type: str (e.g. "HR Interview", "Technical Interview")
            - completed_at: str (ISO date)
            - overall_score: float or None
            - strengths: list[str]
            - weaknesses: list[str]
            - session_id: str
    """
    try:
        html_body = _render_template(session_summary)
        session_type = session_summary.get("session_type", "Interview")
        subject = f"Session Complete: Your {session_type} Summary"

        await email_client.send_email(
            to=user_email,
            subject=subject,
            html_body=html_body,
            text_body=_build_plain_text(session_summary),
        )
        logger.info(
            "Session completion email sent to %s for session %s",
            user_email,
            session_summary.get("session_id"),
        )
    except Exception as e:
        logger.error(
            "Failed to send session completion email to %s: %s",
            user_email,
            str(e),
        )


def _build_plain_text(session_summary: dict) -> str:
    """Build a plain-text fallback for the session completion email."""
    session_type = session_summary.get("session_type", "Interview")
    overall_score = session_summary.get("overall_score")
    strengths = session_summary.get("strengths", [])
    weaknesses = session_summary.get("weaknesses", [])

    score_text = f"{int(overall_score)}/100" if overall_score is not None else "N/A"
    strengths_text = ", ".join(strengths[:2]) if strengths else "Keep practicing!"
    improvement_text = weaknesses[0] if weaknesses else "No specific areas flagged"

    settings = get_settings()
    frontend_url = settings.get_resolved_frontend_url()
    session_id = session_summary.get("session_id", "")
    report_url = f"{frontend_url}/history/{session_id}"

    return (
        f"Your {session_type} session is complete!\n\n"
        f"Overall Score: {score_text}\n"
        f"Strengths: {strengths_text}\n"
        f"Area to improve: {improvement_text}\n\n"
        f"View your full report: {report_url}\n"
    )
