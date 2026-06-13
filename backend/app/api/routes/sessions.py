"""Technical interview session API routes.

Provides endpoints for creating technical interview sessions,
submitting answers with technical evaluation, retrieving score breakdowns,
and generating follow-up questions for weak areas.

Requirements: 5.1, 5.2, 5.3, 5.4
"""

import logging
from uuid import UUID

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.api.schemas.session_schemas import (
    CreateTechnicalSessionRequest,
    CreateTechnicalSessionResponse,
    FollowUpRequest,
    FollowUpResponse,
    SubmitTechnicalAnswerResponse,
    TechnicalEvaluationResponse,
)
from app.dependencies import CurrentUserDep
from app.services.technical_session_service import (
    TechnicalSessionNotFoundError,
    TechnicalSessionService,
    TechnicalSessionServiceError,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sessions/technical", tags=["Technical Interview Sessions"])


def _get_technical_session_service() -> TechnicalSessionService:
    """Get a TechnicalSessionService instance."""
    return TechnicalSessionService()


@router.post(
    "",
    response_model=CreateTechnicalSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new technical interview session",
)
async def create_technical_session(
    request: CreateTechnicalSessionRequest,
    current_user_id: CurrentUserDep,
):
    """Create a new technical interview session with topic-specific questions.

    Generates questions based on the specified technical topic and difficulty level.
    Returns the session with generated questions.

    Requirement 5.1: Produce topic-specific technical questions at selected difficulty.
    """
    service = _get_technical_session_service()

    try:
        result = await service.create_technical_session(
            user_id=current_user_id,
            topic=request.topic.value,
            difficulty=request.difficulty.value,
            role=request.role,
            num_questions=request.num_questions,
        )
    except TechnicalSessionServiceError as e:
        logger.error("Failed to create technical session: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create technical interview session: {e}",
        )

    return result


@router.post(
    "/{session_id}/answers",
    response_model=SubmitTechnicalAnswerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a technical answer with audio recording",
)
async def submit_technical_answer(
    session_id: UUID,
    current_user_id: CurrentUserDep,
    audio: UploadFile = File(..., description="Audio recording of the answer"),
    question_index: int = Form(..., description="Zero-based question index"),
    question_text: str = Form(..., description="The question text being answered"),
):
    """Submit a technical answer for evaluation.

    Accepts audio as multipart form data, transcribes it, and evaluates
    technical accuracy, completeness, and communication clarity.

    Requirement 5.2: Evaluate technical accuracy, completeness, and communication.
    """
    audio_data = await audio.read()

    if not audio_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio file is empty",
        )

    filename = audio.filename or "audio.webm"
    service = _get_technical_session_service()

    try:
        result = await service.submit_technical_answer(
            user_id=current_user_id,
            session_id=session_id,
            question_index=question_index,
            question_text=question_text,
            audio_data=audio_data,
            audio_filename=filename,
        )
    except TechnicalSessionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or access denied",
        )
    except TechnicalSessionServiceError as e:
        logger.error(
            "Failed to submit technical answer for session %s: %s",
            session_id,
            str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process technical answer. Please try again.",
        )

    return result


@router.get(
    "/{session_id}/evaluation",
    response_model=TechnicalEvaluationResponse,
    summary="Get technical evaluation score breakdown",
)
async def get_technical_evaluation(
    session_id: UUID,
    current_user_id: CurrentUserDep,
):
    """Get the full evaluation breakdown for a technical interview session.

    Returns separate scores for technical accuracy, completeness, and
    communication for each answered question, plus average scores.

    Requirement 5.4: Display evaluation score breakdown.
    """
    service = _get_technical_session_service()

    try:
        result = await service.get_evaluation(
            user_id=current_user_id,
            session_id=session_id,
        )
    except TechnicalSessionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or access denied",
        )
    except TechnicalSessionServiceError as e:
        logger.error(
            "Failed to get evaluation for session %s: %s",
            session_id,
            str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve evaluation. Please try again.",
        )

    return result


@router.post(
    "/{session_id}/follow-up",
    response_model=FollowUpResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a follow-up question for weak area",
)
async def generate_follow_up(
    session_id: UUID,
    request: FollowUpRequest,
    current_user_id: CurrentUserDep,
):
    """Generate a follow-up question targeting a weak area in the candidate's answer.

    When the evaluation identifies incomplete or incorrect answers, this endpoint
    generates a probing follow-up question for that specific weak area.

    Requirement 5.3: Generate follow-up question probing the weak area.
    """
    service = _get_technical_session_service()

    try:
        result = await service.generate_follow_up(
            user_id=current_user_id,
            session_id=session_id,
            question_index=request.question_index,
            weak_area=request.weak_area,
        )
    except TechnicalSessionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or access denied",
        )
    except TechnicalSessionServiceError as e:
        logger.error(
            "Failed to generate follow-up for session %s: %s",
            session_id,
            str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate follow-up question. Please try again.",
        )

    return result
