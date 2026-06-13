"""Session service for interview session lifecycle management.

Orchestrates session creation, answer submission, and session completion.
Coordinates between question generation, transcription, and persistence.

Requirements: 4.2, 4.3, 4.6, 16.1
"""

import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from app.models.session import (
    Difficulty,
    InterviewType,
    SessionStatus,
    SessionType,
)
from app.repositories.session_repository import SessionRepository, RepositoryError
from app.services.question_generator import QuestionGenerator
from app.services.transcription_service import TranscriptionService, TranscriptionError

logger = logging.getLogger(__name__)


class SessionServiceError(Exception):
    """Raised when a session operation fails."""

    pass


class SessionNotFoundError(SessionServiceError):
    """Raised when a session is not found or not owned by user."""

    pass


class SessionService:
    """Service managing interview session lifecycle.

    Handles:
    - Creating new sessions with generated questions
    - Submitting answers (audio transcription)
    - Completing sessions with aggregate score computation
    """

    def __init__(
        self,
        repository: Optional[SessionRepository] = None,
        question_generator: Optional[QuestionGenerator] = None,
        transcription_service: Optional[TranscriptionService] = None,
    ) -> None:
        """Initialize the session service with its dependencies.

        Args:
            repository: Session repository instance. Creates default if None.
            question_generator: Question generator instance. Creates default if None.
            transcription_service: Transcription service instance. Creates default if None.
        """
        self._repository = repository or SessionRepository()
        self._question_generator = question_generator or QuestionGenerator()
        self._transcription = transcription_service or TranscriptionService()

    async def create_session(
        self,
        user_id: str,
        interview_type: InterviewType,
        role: str,
        topic: Optional[str] = None,
        difficulty: Optional[Difficulty] = None,
        num_questions: int = 5,
    ) -> dict:
        """Create a new interview session with generated questions.

        Flow:
        1. Generate questions via QuestionGenerator
        2. Create session record in database
        3. Store generated questions
        4. Return session with questions

        Args:
            user_id: The authenticated user's ID.
            interview_type: Type of interview (HR, Technical, etc.).
            role: Target job role for question generation.
            topic: Optional topic for technical interviews.
            difficulty: Optional difficulty level.
            num_questions: Number of questions to generate.

        Returns:
            Dict with session data and questions.

        Raises:
            SessionServiceError: If session creation fails.
        """
        logger.info(
            "Creating interview session: user=%s, type=%s, role=%s",
            user_id,
            interview_type.value,
            role,
        )

        try:
            # Step 1: Generate questions
            logger.info(
                "Step 1: Generating questions type=%s, role=%s, topic=%s, difficulty=%s",
                interview_type.value,
                role,
                topic,
                difficulty.value if difficulty else None,
            )
            result = await self._question_generator.generate_questions(
                interview_type=interview_type.value,
                role=role,
                topic=topic,
                difficulty=difficulty.value if difficulty else None,
                num_questions=num_questions,
            )
            logger.info(
                "Step 1 complete: got %d questions from source=%s",
                len(result.questions),
                result.source,
            )

            # Step 2: Create session record
            # Only include non-None optional fields to avoid Supabase
            # rejecting explicit null for enum-typed columns.
            session_data: dict = {
                "user_id": user_id,
                "session_type": SessionType.INTERVIEW.value,
                "interview_type": interview_type.value,
                "role": role,
                "status": SessionStatus.IN_PROGRESS.value,
            }
            if topic is not None:
                session_data["topic"] = topic
            if difficulty is not None:
                session_data["difficulty"] = difficulty.value

            logger.info("Step 2: Inserting session record: %s", session_data)
            session = self._repository.create_session(session_data)
            logger.info("Step 2 complete: session id=%s", session.get("id"))

            # Step 3: Store generated questions as metadata on the session
            # (stored in-memory; the questions are returned directly to the client
            # and will be referenced by index when answers are submitted)
            logger.info(
                "Session created: id=%s, questions=%d, source=%s",
                session["id"],
                len(result.questions),
                result.source,
            )

            return {
                "session": session,
                "questions": [q.model_dump() for q in result.questions],
                "question_source": result.source,
                "fallback_used": result.fallback_used,
            }

        except RepositoryError as e:
            logger.error("Repository error creating session: %s", str(e), exc_info=True)
            raise SessionServiceError(f"Failed to create session: {e}") from e
        except Exception as e:
            logger.error("Unexpected error creating session: %s", str(e), exc_info=True)
            raise SessionServiceError(f"Session creation failed: {e}") from e

    async def submit_answer(
        self,
        user_id: str,
        session_id: UUID,
        question_index: int,
        question_text: str,
        audio_data: bytes,
        audio_filename: str = "audio.webm",
    ) -> dict:
        """Submit an answer for a session question.

        Flow:
        1. Verify session exists and belongs to user
        2. Transcribe audio via Groq Speech-to-Text
        3. Create answer record with transcript
        4. Return answer with transcript

        Note: Speech analysis, confidence scoring, and AI feedback
        are handled by separate services in subsequent tasks.

        Args:
            user_id: The authenticated user's ID.
            session_id: The session UUID.
            question_index: Zero-based index of the question being answered.
            question_text: The question text for reference.
            audio_data: Raw audio bytes from recording.
            audio_filename: Filename hint for audio format.

        Returns:
            Dict with answer data including transcript.

        Raises:
            SessionNotFoundError: If session not found or not owned by user.
            SessionServiceError: If answer submission fails.
        """
        logger.info(
            "Submitting answer: session=%s, question_index=%d",
            session_id,
            question_index,
        )

        # Step 1: Verify session ownership and status
        session = self._repository.get_session(session_id, user_id)
        if not session:
            raise SessionNotFoundError(
                f"Session {session_id} not found or access denied"
            )

        if session.get("status") == SessionStatus.COMPLETED.value:
            raise SessionServiceError("Cannot submit answers to a completed session")

        # Step 2: Transcribe audio
        try:
            transcript = await self._transcription.transcribe_audio(
                audio_data=audio_data,
                filename=audio_filename,
            )
        except TranscriptionError as e:
            logger.error(
                "Transcription failed for session=%s, question=%d: %s",
                session_id,
                question_index,
                str(e),
            )
            raise SessionServiceError(f"Transcription failed: {e}") from e

        # Step 3: Create answer record
        answer_data = {
            "session_id": str(session_id),
            "question_index": question_index,
            "question_text": question_text,
            "transcript": transcript,
        }

        try:
            answer = self._repository.create_answer(answer_data)
        except RepositoryError as e:
            logger.error("Failed to save answer: %s", str(e))
            raise SessionServiceError(f"Failed to save answer: {e}") from e

        logger.info(
            "Answer submitted: id=%s, transcript_length=%d",
            answer.get("id"),
            len(transcript),
        )

        return {
            "answer": answer,
            "transcript": transcript,
        }

    async def complete_session(self, user_id: str, session_id: UUID) -> dict:
        """Complete an interview session and compute aggregate scores.

        Flow:
        1. Verify session exists and belongs to user
        2. Get all answers for the session
        3. Compute aggregate scores from answers
        4. Update session as completed with scores and timestamp
        5. Return final session state

        Args:
            user_id: The authenticated user's ID.
            session_id: The session UUID.

        Returns:
            Dict with completed session data and summary.

        Raises:
            SessionNotFoundError: If session not found or not owned by user.
            SessionServiceError: If completion fails.
        """
        logger.info("Completing session: id=%s, user=%s", session_id, user_id)

        # Step 1: Verify session ownership
        session = self._repository.get_session(session_id, user_id)
        if not session:
            raise SessionNotFoundError(
                f"Session {session_id} not found or access denied"
            )

        if session.get("status") == SessionStatus.COMPLETED.value:
            raise SessionServiceError("Session is already completed")

        # Step 2: Get all answers
        try:
            answers = self._repository.get_session_answers(session_id, user_id)
        except RepositoryError as e:
            raise SessionServiceError(f"Failed to retrieve answers: {e}") from e

        # Step 3: Compute aggregate scores from available answer data
        scores = self._compute_aggregate_scores(answers)

        # Step 4: Update session as completed
        now = datetime.now(timezone.utc).isoformat()
        updates = {
            "status": SessionStatus.COMPLETED.value,
            "completed_at": now,
            **scores,
        }

        # Calculate duration if session has created_at
        if session.get("created_at"):
            try:
                created_at = datetime.fromisoformat(
                    session["created_at"].replace("Z", "+00:00")
                )
                duration = int(
                    (datetime.now(timezone.utc) - created_at).total_seconds()
                )
                updates["duration_seconds"] = duration
            except (ValueError, TypeError):
                pass

        try:
            completed_session = self._repository.update_session(
                session_id, user_id, updates
            )
        except RepositoryError as e:
            raise SessionServiceError(f"Failed to complete session: {e}") from e

        logger.info(
            "Session completed: id=%s, answers=%d, overall_score=%s",
            session_id,
            len(answers),
            scores.get("overall_score"),
        )

        return {
            "session": completed_session,
            "total_answers": len(answers),
            "scores": scores,
        }

    def _compute_aggregate_scores(self, answers: list[dict]) -> dict:
        """Compute aggregate scores from session answers.

        Averages available scores across all answers. Returns None
        for scores where no data is available yet.

        Args:
            answers: List of answer records.

        Returns:
            Dict with overall_score, confidence_score, communication_score.
        """
        if not answers:
            return {
                "overall_score": None,
                "confidence_score": None,
                "communication_score": None,
            }

        communication_scores = [
            a["communication_score"]
            for a in answers
            if a.get("communication_score") is not None
        ]
        confidence_scores = [
            a["confidence_score"]
            for a in answers
            if a.get("confidence_score") is not None
        ]

        avg_communication = (
            int(sum(communication_scores) / len(communication_scores))
            if communication_scores
            else None
        )
        avg_confidence = (
            int(sum(confidence_scores) / len(confidence_scores))
            if confidence_scores
            else None
        )

        # Overall score is the average of available sub-scores
        available_scores = [
            s for s in [avg_communication, avg_confidence] if s is not None
        ]
        overall_score = (
            int(sum(available_scores) / len(available_scores))
            if available_scores
            else None
        )

        return {
            "overall_score": overall_score,
            "confidence_score": avg_confidence,
            "communication_score": avg_communication,
        }
