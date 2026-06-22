"""Common FastAPI dependencies for dependency injection."""

from typing import Annotated

from fastapi import Depends, HTTPException

from app.api.middleware.auth_middleware import get_current_user_id
from app.config import Settings, get_settings


def get_current_settings() -> Settings:
    """Dependency to provide application settings."""
    return get_settings()


def require_email_enabled() -> None:
    """Dependency that checks if email functionality is available.

    Raises HTTP 503 if SMTP is not properly configured, preventing
    email-sending endpoints from executing when email is unavailable.
    """
    settings = get_settings()
    if not settings.get_smtp_enabled():
        raise HTTPException(
            status_code=503,
            detail="Email functionality is unavailable",
        )


SettingsDep = Annotated[Settings, Depends(get_current_settings)]

CurrentUserDep = Annotated[str, Depends(get_current_user_id)]
