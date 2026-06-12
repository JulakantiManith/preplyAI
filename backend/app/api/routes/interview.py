"""Interview session API routes.

Provides endpoints for creating interview sessions, submitting answers
with audio transcription, and completing sessions.

Requirements: 4.2, 4.3, 4.6, 16.1, 16.3
"""

import logging
from uuid import UUID

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.api.schemas.interview_schemas import (
    CompleteSessionResponse,
    CreateSessionRequest,
    CreateSessionResponse,
    SubmitAnswerResponse,
)
from app.dependencies import CurrentUserDep
from app.models.session import Difficulty, InterviewType
from app.services.session_service import (
    SessionNotFoundError,
    SessionService,
    SessionServiceError,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sessions/interview", tags=["Interview Sessions"])


def _get_session_service() -> SessionService:
    """Get a SessionService instance."""
    return SessionService()


@router.post(
    "",
    response_model=CreateSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new interview session",
)
async def create_interview_session(
    request: CreateSessionRequest,
    current_user_id: CurrentUserDep,
):
    """Create a new interview session with AI-generated questions.

    Generates questions based on the specified interview type, role,
    and optional parameters. Returns the session with questions.
    """
    service = _get_session_service()

    try:
        result = await service.create_session(
            user_id=current_user_id,
            interview_type=request.interview_type,
            role=request.role,
            topic=request.topic,
            difficulty=request.difficulty,
            num_questions=request.num_questions,
        )
    except SessionServiceError as e:
        logger.error("Failed to create session: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create interview session: {e}",
        )

    return result


@router.post(
    "/{session_id}/answers",
    response_model=SubmitAnswerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit an answer with audio recording",
)
async def submit_answer(
    session_id: UUID,
    current_user_id: CurrentUserDep,
    audio: UploadFile = File(..., description="Audio recording of the answer"),
    question_index: int = Form(..., description="Zero-based question index"),
    question_text: str = Form(..., description="The question text being answered"),
):
    """Submit an answer to a session question with audio recording.

    Accepts audio as multipart form data, transcribes it via Whisper,
    and stores the answer with transcript. Speech analysis and AI feedback
    are computed asynchronously by separate services.
    """
    # Read audio file data
    audio_data = await audio.read()

    if not audio_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio file is empty",
        )

    # Use original filename or default
    filename = audio.filename or "audio.webm"

    service = _get_session_service()

    try:
        result = await service.submit_answer(
            user_id=current_user_id,
            session_id=session_id,
            question_index=question_index,
            question_text=question_text,
            audio_data=audio_data,
            audio_filename=filename,
        )
    except SessionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or access denied",
        )
    except SessionServiceError as e:
        logger.error(
            "Failed to submit answer for session %s: %s", session_id, str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process answer. Please try again.",
        )

    return result


@router.post(
    "/{session_id}/complete",
    response_model=CompleteSessionResponse,
    summary="Complete an interview session",
)
async def complete_session(
    session_id: UUID,
    current_user_id: CurrentUserDep,
):
    """Complete an interview session and get the score report.

    Marks the session as completed, computes aggregate scores from
    all submitted answers, and returns a summary report.
    """
    service = _get_session_service()

    try:
        result = await service.complete_session(
            user_id=current_user_id,
            session_id=session_id,
        )
    except SessionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or access denied",
        )
    except SessionServiceError as e:
        logger.error(
            "Failed to complete session %s: %s", session_id, str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete session. Please try again.",
        )

    return result
