"""Profile service for managing user profiles and resume uploads.

Requirements: 2.1, 2.2, 2.3, 2.4, 16.2, 16.3, 16.4
"""

import logging
import uuid
from typing import Any, Optional

from fastapi import HTTPException, UploadFile, status

from app.integrations.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

# 10 MB file size limit
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024

# Retry configuration for write operations - Requirement 16.3
WRITE_MAX_RETRIES = 1

# Allowed MIME types for resume uploads
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


class ProfileService:
    """Service layer for profile and resume operations.

    All write operations implement retry-once logic per Requirement 16.3.
    All queries filter by user_id for data isolation per Requirement 16.4.
    """

    def __init__(self):
        self._client = get_supabase_client()

    def _retry_write(self, operation_name: str, operation_fn: Any) -> Any:
        """Execute a write operation with retry-once logic.

        Per Requirement 16.3: retry the operation once on failure,
        display error if retry also fails.

        Args:
            operation_name: Descriptive name for logging.
            operation_fn: Callable that performs the write operation.

        Returns:
            Result of the operation.

        Raises:
            HTTPException: If the operation fails after retry.
        """
        last_error: Optional[Exception] = None

        for attempt in range(WRITE_MAX_RETRIES + 1):
            try:
                result = operation_fn()
                return result
            except HTTPException:
                raise
            except Exception as e:
                last_error = e
                if attempt < WRITE_MAX_RETRIES:
                    logger.warning(
                        "Database write failed for '%s' (attempt %d/%d), retrying: %s",
                        operation_name,
                        attempt + 1,
                        WRITE_MAX_RETRIES + 1,
                        str(e),
                    )
                else:
                    logger.error(
                        "Database write failed for '%s' after %d attempts: %s",
                        operation_name,
                        WRITE_MAX_RETRIES + 1,
                        str(e),
                    )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to {operation_name} after retrying. Please try again later.",
        )

    def get_profile(self, user_id: str) -> dict:
        """Get the profile for the given user.

        Args:
            user_id: The authenticated user's UUID.

        Returns:
            Profile data dictionary.

        Raises:
            HTTPException: 404 if profile not found.
        """
        try:
            response = (
                self._client.table("profiles")
                .select("*")
                .eq("user_id", user_id)
                .execute()
            )

            if not response.data:
                # Return a default empty profile for the user
                return {
                    "id": None,
                    "user_id": user_id,
                    "target_role": None,
                    "experience_level": None,
                    "skills": None,
                    "theme_preference": None,
                    "updated_at": None,
                }

            return response.data[0]

        except HTTPException:
            raise
        except Exception as e:
            logger.error("Failed to get profile for user %s: %s", user_id, str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve profile",
            ) from e

    def update_profile(self, user_id: str, data: dict) -> dict:
        """Update the profile for the given user.

        Uses retry-once logic for write operations per Requirement 16.3.

        Args:
            user_id: The authenticated user's UUID.
            data: Dictionary of fields to update.

        Returns:
            Updated profile data dictionary.

        Raises:
            HTTPException: 500 on database errors after retry.
        """
        try:
            # Remove None values — only update provided fields
            update_data = {k: v for k, v in data.items() if v is not None}

            if not update_data:
                return self.get_profile(user_id)

            # Check if profile exists
            existing = (
                self._client.table("profiles")
                .select("id")
                .eq("user_id", user_id)
                .execute()
            )

            if existing.data:
                # Update existing profile with retry
                def _update():
                    response = (
                        self._client.table("profiles")
                        .update(update_data)
                        .eq("user_id", user_id)
                        .execute()
                    )
                    if not response.data:
                        raise Exception("No data returned from profile update")
                    return response.data[0]

                return self._retry_write("update profile", _update)
            else:
                # Create new profile with retry
                update_data["user_id"] = user_id

                def _insert():
                    response = (
                        self._client.table("profiles")
                        .insert(update_data)
                        .execute()
                    )
                    if not response.data:
                        raise Exception("No data returned from profile insert")
                    return response.data[0]

                return self._retry_write("create profile", _insert)

        except HTTPException:
            raise
        except Exception as e:
            logger.error("Failed to update profile for user %s: %s", user_id, str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update profile",
            ) from e

    async def upload_resume(self, user_id: str, file: UploadFile) -> dict:
        """Upload a resume file and store metadata.

        Uses retry-once logic for write operations per Requirement 16.3.
        Files stored under user_id path for data isolation per Requirement 16.2.

        Args:
            user_id: The authenticated user's UUID.
            file: The uploaded file object.

        Returns:
            Resume metadata dictionary.

        Raises:
            HTTPException: 400 if file validation fails, 500 on storage errors after retry.
        """
        # Validate MIME type
        if file.content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF and DOCX files are accepted",
            )

        # Read file content and validate size
        content = await file.read()
        file_size = len(content)

        if file_size > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds the 10 MB limit",
            )

        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty",
            )

        try:
            # Generate unique file path scoped to user (Requirement 16.2)
            file_ext = file.filename.rsplit(".", 1)[-1] if file.filename else "pdf"
            unique_name = f"{uuid.uuid4().hex}.{file_ext}"
            file_path = f"{user_id}/{unique_name}"

            # Upload to Supabase Storage with retry
            def _upload_storage():
                self._client.storage.from_("resumes").upload(
                    path=file_path,
                    file=content,
                    file_options={"content-type": file.content_type},
                )

            self._retry_write("upload resume to storage", _upload_storage)

            # Store metadata in resumes table with retry
            resume_data = {
                "user_id": user_id,
                "file_path": file_path,
                "file_name": file.filename or unique_name,
                "file_size": file_size,
                "extraction_status": "pending",
            }

            def _insert_metadata():
                response = (
                    self._client.table("resumes")
                    .insert(resume_data)
                    .execute()
                )
                if not response.data:
                    raise Exception("No data returned from resume metadata insert")
                return response.data[0]

            return self._retry_write("save resume metadata", _insert_metadata)

        except HTTPException:
            raise
        except Exception as e:
            logger.error("Failed to upload resume for user %s: %s", user_id, str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload resume",
            ) from e

    def get_resume_metadata(self, user_id: str) -> dict | None:
        """Get the most recent resume metadata for the user.

        Args:
            user_id: The authenticated user's UUID.

        Returns:
            Resume metadata dictionary or None if no resume exists.

        Raises:
            HTTPException: 404 if no resume found, 500 on errors.
        """
        try:
            response = (
                self._client.table("resumes")
                .select("*")
                .eq("user_id", user_id)
                .order("uploaded_at", desc=True)
                .limit(1)
                .execute()
            )

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No resume found for this user",
                )

            return response.data[0]

        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "Failed to get resume metadata for user %s: %s", user_id, str(e)
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve resume metadata",
            ) from e


def get_profile_service() -> ProfileService:
    """Factory function for ProfileService dependency injection."""
    return ProfileService()
