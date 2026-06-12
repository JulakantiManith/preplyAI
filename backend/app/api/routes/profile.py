"""Profile API routes."""

import logging

from fastapi import APIRouter, File, UploadFile, status

from app.api.schemas.profile_schemas import (
    ProfileResponse,
    ProfileUpdateRequest,
    ResumeMetadataResponse,
    ResumeUploadResponse,
)
from app.dependencies import CurrentUserDep
from app.services.profile_service import get_profile_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get(
    "",
    response_model=ProfileResponse,
    summary="Get current user profile",
)
async def get_profile(current_user_id: CurrentUserDep):
    """Get the authenticated user's profile information.

    Returns the user's target role, experience level, skills,
    and theme preference.
    """
    profile_service = get_profile_service()
    result = profile_service.get_profile(user_id=current_user_id)
    return ProfileResponse(**result)


@router.put(
    "",
    response_model=ProfileResponse,
    summary="Update user profile",
)
async def update_profile(
    current_user_id: CurrentUserDep,
    request: ProfileUpdateRequest,
):
    """Update the authenticated user's profile information.

    Only provided fields will be updated; omitted fields are left unchanged.
    """
    profile_service = get_profile_service()
    result = profile_service.update_profile(
        user_id=current_user_id,
        data=request.model_dump(exclude_unset=True),
    )
    return ProfileResponse(**result)


@router.post(
    "/resume",
    response_model=ResumeUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload resume file",
)
async def upload_resume(
    current_user_id: CurrentUserDep,
    file: UploadFile = File(..., description="Resume file (PDF or DOCX, max 10 MB)"),
):
    """Upload a resume file for the authenticated user.

    Accepts PDF and DOCX files up to 10 MB. The file is stored
    in Supabase Storage and associated with the user's profile.
    """
    profile_service = get_profile_service()
    result = await profile_service.upload_resume(
        user_id=current_user_id,
        file=file,
    )
    return ResumeUploadResponse(**result)


@router.get(
    "/resume",
    response_model=ResumeMetadataResponse,
    summary="Get resume metadata",
)
async def get_resume_metadata(current_user_id: CurrentUserDep):
    """Get the metadata of the authenticated user's most recent resume.

    Returns file information and extraction status.
    """
    profile_service = get_profile_service()
    result = profile_service.get_resume_metadata(user_id=current_user_id)
    return ResumeMetadataResponse(**result)
