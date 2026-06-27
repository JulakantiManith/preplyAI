"""Pydantic schemas for profile endpoints."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class ProfileUpdateRequest(BaseModel):
    """Request schema for updating user profile."""

    target_role: str | None = Field(
        default=None, max_length=200, description="Target job role"
    )
    experience_level: str | None = Field(
        default=None, max_length=50, description="Experience level"
    )
    skills: list[str] | None = Field(
        default=None, max_length=50, description="List of skills"
    )
    email_notifications_enabled: bool | None = Field(
        default=None, description="Enable session completion email notifications"
    )

    @field_validator("target_role")
    @classmethod
    def target_role_not_blank(cls, v: str | None) -> str | None:
        """Ensure target_role is not just whitespace if provided."""
        if v is not None and not v.strip():
            raise ValueError("Target role cannot be blank")
        return v.strip() if v else v

    @field_validator("experience_level")
    @classmethod
    def experience_level_valid(cls, v: str | None) -> str | None:
        """Validate experience level if provided."""
        valid_levels = {"beginner", "intermediate", "advanced", "senior", "lead"}
        if v is not None:
            if not v.strip():
                raise ValueError("Experience level cannot be blank")
            if v.strip().lower() not in valid_levels:
                raise ValueError(
                    f"Experience level must be one of: {', '.join(sorted(valid_levels))}"
                )
            return v.strip().lower()
        return v

    @field_validator("skills")
    @classmethod
    def skills_not_empty_strings(cls, v: list[str] | None) -> list[str] | None:
        """Ensure skills list contains no empty strings."""
        if v is not None:
            cleaned = [s.strip() for s in v if s.strip()]
            if len(v) > 0 and len(cleaned) == 0:
                raise ValueError("Skills list cannot contain only blank entries")
            return cleaned
        return v


class ProfileResponse(BaseModel):
    """Response schema for user profile."""

    id: str | None = None
    user_id: str
    target_role: str | None = None
    experience_level: str | None = None
    skills: list[str] | None = None
    theme_preference: str | None = None
    email_notifications_enabled: bool = True
    updated_at: str | None = None


class ResumeUploadResponse(BaseModel):
    """Response schema for resume upload."""

    id: str
    user_id: str
    file_path: str
    file_name: str
    file_size: int
    extraction_status: str
    uploaded_at: str


class ResumeMetadataResponse(BaseModel):
    """Response schema for resume metadata."""

    id: str
    user_id: str
    file_path: str
    file_name: str
    file_size: int
    extracted_data: dict | None = None
    extraction_confidence: float | None = None
    user_confirmed: bool | None = None
    extraction_status: str
    uploaded_at: str
