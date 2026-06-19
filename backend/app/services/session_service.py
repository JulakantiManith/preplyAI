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
from app.models.answer import SpeechMetrics
from app.repositories.session_repository import SessionRepository, RepositoryError
from app.services.question_generator import QuestionGenerator
from app.services.transcription_service import TranscriptionService, TranscriptionError
from app.services.ai_feedback_service import AIFeedbackService, SessionData, AnswerData
from app.services.speech_analysis_service import SpeechAnalysisService

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
        feedback_service: Optional[AIFeedbackService] = None,
        speech_analysis_service: Optional[SpeechAnalysisService] = None,
    ) -> None:
        """Initialize the session service with its dependencies.

        Args:
            repository: Session repository instance. Creates default if None.
            question_generator: Question generator instance. Creates default if None.
            transcription_service: Transcription service instance. Creates default if None.
            feedback_service: AI feedback service instance. Creates default if None.
            speech_analysis_service: Speech analysis service. Creates default if None.
        """
        self._repository = repository or SessionRepository()
        self._question_generator = question_generator or QuestionGenerator()
        self._transcription = transcription_service or TranscriptionService()
        self._feedback_service = feedback_service or AIFeedbackService()
        self._speech_analysis = speech_analysis_service or SpeechAnalysisService()

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

        # Step 2: Transcribe audio (with word timestamps)
        try:
            transcription_result = await self._transcription.transcribe_audio_detailed(
                audio_data=audio_data,
                filename=audio_filename,
            )
            transcript = transcription_result.text
        except TranscriptionError as e:
            logger.error(
                "Transcription failed for session=%s, question=%d: %s",
                session_id,
                question_index,
                str(e),
            )
            raise SessionServiceError(f"Transcription failed: {e}") from e

        # Step 3: Run speech analysis on the transcript
        speech_metrics = None
        confidence_result = None
        # Use actual duration from word timestamps, fallback to audio size estimate
        actual_duration = transcription_result.duration
        if actual_duration <= 0:
            actual_duration = max(len(audio_data) / 16000, 1.0)

        # Analyze hesitations from word timestamp gaps
        hesitation_analysis = self._transcription.analyze_hesitations(
            transcription_result.words
        )
        detected_hesitations = hesitation_analysis.hesitation_count

        if transcript and len(transcript.strip()) > 0:
            try:
                speech_metrics = self._speech_analysis.analyze(transcript, actual_duration)
                # Override filler count with hesitation-detected count (more accurate)
                # The transcript doesn't contain fillers, but timing gaps reveal them
                if detected_hesitations > speech_metrics.filler_word_count:
                    speech_metrics.filler_word_count = detected_hesitations
                    # Recalculate communication score:
                    # Penalize based on filler/hesitation ratio
                    total_words = max(speech_metrics.total_words, 1)
                    filler_ratio = detected_hesitations / total_words
                    # Reduce communication score proportionally
                    filler_penalty = int(filler_ratio * 100 * 1.5)  # 1.5x weight
                    speech_metrics.communication_score = max(
                        0, speech_metrics.communication_score - filler_penalty
                    )
                logger.info(
                    "Speech analysis: wpm=%d, fillers=%d (detected_hesitations=%d), comm_score=%d",
                    speech_metrics.wpm,
                    speech_metrics.filler_word_count,
                    detected_hesitations,
                    speech_metrics.communication_score,
                )
            except Exception as e:
                logger.warning("Speech analysis failed (non-fatal): %s", str(e))

            # Step 4: Run confidence analysis
            if speech_metrics:
                try:
                    from app.services.confidence_analyzer import ConfidenceAnalyzer
                    analyzer = ConfidenceAnalyzer()

                    # Use the HIGHER of: timing-gap hesitations OR text-detected fillers
                    # This ensures fillers that Whisper preserved in text are counted
                    effective_hesitations = max(
                        detected_hesitations,
                        speech_metrics.filler_word_count
                    )
                    total_words = max(speech_metrics.total_words, 1)

                    # Pause frequency from timing analysis
                    pause_frequency = (
                        hesitation_analysis.avg_pause_duration
                        if hesitation_analysis.avg_pause_duration > 0
                        else (speech_metrics.avg_pause_duration / 2.0)
                    )

                    # Speech flow: penalized by filler/hesitation ratio
                    filler_ratio = effective_hesitations / total_words
                    speech_flow = max(0.0, min(1.0, 1.0 - filler_ratio * 4))

                    # Response completeness
                    completeness = min(1.0, total_words / (actual_duration * 1.5))

                    confidence_result = analyzer.analyze(
                        transcript=transcript,
                        hesitation_count=effective_hesitations,
                        pause_frequency=pause_frequency,
                        speech_flow_score=speech_flow,
                        response_completeness=completeness,
                    )
                    logger.info(
                        "Confidence analysis: score=%d (hesitations=%d, fillers_text=%d, timing_gaps=%d)",
                        confidence_result.score,
                        effective_hesitations,
                        speech_metrics.filler_word_count,
                        detected_hesitations,
                    )
                except Exception as e:
                    logger.warning("Confidence analysis failed (non-fatal): %s", str(e))

        # Step 5: Create answer record with analysis results
        answer_data: dict = {
            "session_id": str(session_id),
            "question_index": question_index,
            "question_text": question_text,
            "transcript": transcript,
        }

        if speech_metrics:
            answer_data["wpm"] = speech_metrics.wpm
            answer_data["total_words"] = speech_metrics.total_words
            answer_data["filler_word_count"] = speech_metrics.filler_word_count
            answer_data["speaking_duration"] = speech_metrics.speaking_duration
            answer_data["avg_pause_duration"] = speech_metrics.avg_pause_duration
            answer_data["communication_score"] = speech_metrics.communication_score

        if confidence_result:
            answer_data["confidence_score"] = confidence_result.score

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
            # Session already completed — return existing data
            logger.info("Session %s already completed, returning existing data", session_id)
            try:
                answers = self._repository.get_session_answers(session_id, user_id)
            except RepositoryError:
                answers = []
            scores = {
                "overall_score": session.get("overall_score"),
                "confidence_score": session.get("confidence_score"),
                "communication_score": session.get("communication_score"),
            }
            # Try to generate feedback even for already-completed sessions
            feedback_data = None
            try:
                feedback_data = await self._generate_session_feedback(
                    session=session,
                    answers=answers,
                    session_id=str(session_id),
                )
                # Persist if not already saved
                try:
                    self._repository.create_session_feedback(session_id, feedback_data)
                except RepositoryError:
                    pass  # May already exist
            except Exception as e:
                logger.warning(
                    "Failed to generate feedback for already-completed session %s: %s",
                    session_id, str(e)
                )
            return {
                "session": session,
                "total_answers": len(answers),
                "scores": scores,
                "feedback": feedback_data,
            }

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

        # Step 5: Generate AI feedback and persist it
        feedback_data = None
        try:
            feedback_data = await self._generate_session_feedback(
                session=session,
                answers=answers,
                session_id=str(session_id),
            )
            logger.info(
                "AI feedback generated for session %s: %d strengths, %d weaknesses, %d recommendations",
                session_id,
                len(feedback_data.get("strengths", [])),
                len(feedback_data.get("weaknesses", [])),
                len(feedback_data.get("recommendations", [])),
            )
            # Persist feedback to session_feedback table
            try:
                self._repository.create_session_feedback(session_id, feedback_data)
                logger.info("Feedback persisted for session %s", session_id)
            except RepositoryError as e:
                logger.warning(
                    "Failed to persist feedback for session %s (non-fatal): %s",
                    session_id,
                    str(e),
                )
        except Exception as e:
            logger.warning(
                "Failed to generate AI feedback for session %s (non-fatal): %s",
                session_id,
                str(e),
            )

        return {
            "session": completed_session,
            "total_answers": len(answers),
            "scores": scores,
            "feedback": feedback_data,
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

    async def _generate_session_feedback(
        self,
        session: dict,
        answers: list[dict],
        session_id: str,
    ) -> dict:
        """Generate AI feedback for a completed session.

        Computes speech metrics from answer transcripts, then calls
        the AI feedback service to generate strengths, weaknesses,
        and recommendations.

        Args:
            session: The session record dict.
            answers: List of answer records with transcripts.
            session_id: Session ID for usage tracking.

        Returns:
            Dict with strengths, weaknesses, recommendations.
        """
        # Build combined transcript from all answers
        transcripts = [a.get("transcript", "") for a in answers if a.get("transcript")]
        combined_transcript = " ".join(transcripts)

        if not combined_transcript.strip():
            # No transcripts available — return minimal algorithmic feedback
            return {
                "strengths": [
                    "Completed all questions in the session",
                    "Showed commitment by finishing the interview",
                ],
                "weaknesses": [
                    "Responses were too brief to analyze in detail",
                    "Consider providing more detailed answers",
                ],
                "recommendations": [
                    "Practice giving more detailed verbal responses",
                    "Try to speak for at least 30-60 seconds per question",
                    "Structure your answers with clear beginning, middle, and end",
                ],
            }

        # Compute speech metrics from combined transcript
        total_duration = sum(
            a.get("speaking_duration", 0) or 0 for a in answers
        )
        if total_duration <= 0:
            # Estimate duration from word count (approx 2.5 words/sec)
            word_count = len(combined_transcript.split())
            total_duration = max(word_count / 2.5, 1.0)

        speech_metrics = self._speech_analysis.analyze(combined_transcript, total_duration)

        # Compute confidence score
        confidence_score = 50  # Default mid-range
        confidence_scores = [
            a["confidence_score"]
            for a in answers
            if a.get("confidence_score") is not None
        ]
        if confidence_scores:
            confidence_score = int(sum(confidence_scores) / len(confidence_scores))

        # Build session data for feedback service
        interview_type_str = session.get("interview_type", "hr")
        try:
            interview_type = InterviewType(interview_type_str)
        except ValueError:
            interview_type = InterviewType.HR

        answer_data_list = [
            AnswerData(
                question_text=a.get("question_text", ""),
                transcript=a.get("transcript", ""),
                communication_score=a.get("communication_score"),
                confidence_score=a.get("confidence_score"),
            )
            for a in answers
        ]

        session_data = SessionData(
            interview_type=interview_type,
            role=session.get("role", ""),
            topic=session.get("topic"),
            difficulty=session.get("difficulty"),
            answers=answer_data_list,
        )

        # Generate feedback (falls back to algorithmic if Gemini fails)
        feedback_report = await self._feedback_service.generate_feedback(
            session_data=session_data,
            speech_metrics=speech_metrics,
            confidence_score=confidence_score,
            session_id=session_id,
        )

        return {
            "strengths": feedback_report.strengths,
            "weaknesses": feedback_report.weaknesses,
            "recommendations": feedback_report.recommendations,
            "technical_evaluation": feedback_report.technical_evaluation,
        }
