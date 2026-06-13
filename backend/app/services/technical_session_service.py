"""Technical interview session service.

Manages the lifecycle of technical interview sessions including creation,
answer submission with technical evaluation, score breakdown retrieval,
and follow-up question generation for weak areas.

Requirements: 5.1, 5.2, 5.3, 5.4
"""

import asyncio
import json
import logging
from typing import Optional
from uuid import UUID

from app.integrations.gemini_client import GeminiClient, GeminiClientError
from app.models.session import (
    Difficulty,
    InterviewType,
    SessionStatus,
    SessionType,
)
from app.repositories.session_repository import RepositoryError, SessionRepository
from app.services.question_generator import QuestionGenerator
from app.services.transcription_service import TranscriptionError, TranscriptionService

logger = logging.getLogger(__name__)

# Timeout for Gemini evaluation calls (seconds)
EVALUATION_TIMEOUT = 45.0


class TechnicalSessionServiceError(Exception):
    """Raised when a technical session operation fails."""

    pass


class TechnicalSessionNotFoundError(TechnicalSessionServiceError):
    """Raised when a session is not found or not owned by user."""

    pass


class TechnicalSessionService:
    """Service managing technical interview session lifecycle.

    Handles:
    - Creating technical sessions with topic-specific questions (Req 5.1)
    - Evaluating answers for technical accuracy, completeness, communication (Req 5.2)
    - Generating follow-up questions for weak areas (Req 5.3)
    - Providing score breakdown (Req 5.4)
    """

    def __init__(
        self,
        repository: Optional[SessionRepository] = None,
        question_generator: Optional[QuestionGenerator] = None,
        transcription_service: Optional[TranscriptionService] = None,
        gemini_client: Optional[GeminiClient] = None,
    ) -> None:
        """Initialize the technical session service.

        Args:
            repository: Session repository instance. Creates default if None.
            question_generator: Question generator instance. Creates default if None.
            transcription_service: Transcription service instance. Creates default if None.
            gemini_client: Gemini client for evaluation. Creates default if None.
        """
        self._repository = repository or SessionRepository()
        self._question_generator = question_generator or QuestionGenerator()
        self._transcription = transcription_service or TranscriptionService()
        self._gemini = gemini_client or GeminiClient()

    async def create_technical_session(
        self,
        user_id: str,
        topic: str,
        difficulty: str,
        role: str,
        num_questions: int = 5,
    ) -> dict:
        """Create a new technical interview session with topic-specific questions.

        Requirement 5.1: Generate topic-specific technical questions at selected difficulty.

        Args:
            user_id: The authenticated user's ID.
            topic: Technical topic for questions.
            difficulty: Difficulty level (beginner, intermediate, advanced).
            role: Target job role.
            num_questions: Number of questions to generate.

        Returns:
            Dict with session data and questions.

        Raises:
            TechnicalSessionServiceError: If session creation fails.
        """
        logger.info(
            "Creating technical session: user=%s, topic=%s, difficulty=%s, role=%s",
            user_id,
            topic,
            difficulty,
            role,
        )

        try:
            # Generate topic-specific technical questions
            result = await self._question_generator.generate_questions(
                interview_type=InterviewType.TECHNICAL.value,
                role=role,
                topic=topic,
                difficulty=difficulty,
                num_questions=num_questions,
            )

            # Create session record
            session_data: dict = {
                "user_id": user_id,
                "session_type": SessionType.INTERVIEW.value,
                "interview_type": InterviewType.TECHNICAL.value,
                "role": role,
                "topic": topic,
                "difficulty": difficulty,
                "status": SessionStatus.IN_PROGRESS.value,
            }

            session = self._repository.create_session(session_data)

            logger.info(
                "Technical session created: id=%s, questions=%d, source=%s",
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
            logger.error("Repository error creating technical session: %s", str(e))
            raise TechnicalSessionServiceError(
                f"Failed to create technical session: {e}"
            ) from e
        except Exception as e:
            logger.error("Unexpected error creating technical session: %s", str(e))
            raise TechnicalSessionServiceError(
                f"Technical session creation failed: {e}"
            ) from e

    async def submit_technical_answer(
        self,
        user_id: str,
        session_id: UUID,
        question_index: int,
        question_text: str,
        audio_data: bytes,
        audio_filename: str = "audio.webm",
    ) -> dict:
        """Submit and evaluate a technical answer.

        Requirement 5.2: Evaluate technical accuracy, completeness, and communication.

        Flow:
        1. Verify session exists and belongs to user
        2. Transcribe audio
        3. Evaluate the technical answer using Gemini
        4. Store answer with evaluation scores
        5. Return evaluation result

        Args:
            user_id: The authenticated user's ID.
            session_id: The session UUID.
            question_index: Zero-based index of the question being answered.
            question_text: The question text for evaluation context.
            audio_data: Raw audio bytes from recording.
            audio_filename: Filename hint for audio format.

        Returns:
            Dict with answer data, transcript, and evaluation scores.

        Raises:
            TechnicalSessionNotFoundError: If session not found or access denied.
            TechnicalSessionServiceError: If answer submission fails.
        """
        logger.info(
            "Submitting technical answer: session=%s, question_index=%d",
            session_id,
            question_index,
        )

        # Verify session ownership and status
        session = self._repository.get_session(session_id, user_id)
        if not session:
            raise TechnicalSessionNotFoundError(
                f"Session {session_id} not found or access denied"
            )

        if session.get("status") == SessionStatus.COMPLETED.value:
            raise TechnicalSessionServiceError(
                "Cannot submit answers to a completed session"
            )

        if session.get("interview_type") != InterviewType.TECHNICAL.value:
            raise TechnicalSessionServiceError(
                "Session is not a technical interview session"
            )

        # Transcribe audio
        try:
            transcript = await self._transcription.transcribe_audio(
                audio_data=audio_data,
                filename=audio_filename,
            )
        except TranscriptionError as e:
            logger.error("Transcription failed for technical answer: %s", str(e))
            raise TechnicalSessionServiceError(f"Transcription failed: {e}") from e

        # Evaluate the technical answer
        topic = session.get("topic", "General")
        difficulty = session.get("difficulty", "intermediate")
        evaluation = await self._evaluate_technical_answer(
            question_text=question_text,
            answer_text=transcript,
            topic=topic,
            difficulty=difficulty,
        )

        # Store answer with evaluation
        answer_data = {
            "session_id": str(session_id),
            "question_index": question_index,
            "question_text": question_text,
            "transcript": transcript,
            "communication_score": evaluation["scores"]["communication"],
            "confidence_score": evaluation["scores"]["technical_accuracy"],
        }

        try:
            answer = self._repository.create_answer(answer_data)
        except RepositoryError as e:
            logger.error("Failed to save technical answer: %s", str(e))
            raise TechnicalSessionServiceError(
                f"Failed to save answer: {e}"
            ) from e

        logger.info(
            "Technical answer submitted: id=%s, accuracy=%d, completeness=%d, communication=%d",
            answer.get("id"),
            evaluation["scores"]["technical_accuracy"],
            evaluation["scores"]["completeness"],
            evaluation["scores"]["communication"],
        )

        return {
            "answer_id": answer["id"],
            "session_id": str(session_id),
            "question_index": question_index,
            "transcript": transcript,
            "scores": evaluation["scores"],
            "feedback": evaluation["feedback"],
            "weak_areas": evaluation["weak_areas"],
        }

    async def get_evaluation(self, user_id: str, session_id: UUID) -> dict:
        """Get the full evaluation breakdown for a technical session.

        Requirement 5.4: Display score breakdown with separate scores for
        technical accuracy, completeness, and communication.

        Args:
            user_id: The authenticated user's ID.
            session_id: The session UUID.

        Returns:
            Dict with evaluations for each answered question and averages.

        Raises:
            TechnicalSessionNotFoundError: If session not found or access denied.
            TechnicalSessionServiceError: If evaluation retrieval fails.
        """
        logger.info("Getting evaluation for session: %s", session_id)

        session = self._repository.get_session(session_id, user_id)
        if not session:
            raise TechnicalSessionNotFoundError(
                f"Session {session_id} not found or access denied"
            )

        if session.get("interview_type") != InterviewType.TECHNICAL.value:
            raise TechnicalSessionServiceError(
                "Session is not a technical interview session"
            )

        # Get all answers
        try:
            answers = self._repository.get_session_answers(session_id, user_id)
        except RepositoryError as e:
            raise TechnicalSessionServiceError(
                f"Failed to retrieve answers: {e}"
            ) from e

        # Build evaluations from stored answer data
        evaluations = []
        total_accuracy = 0
        total_completeness = 0
        total_communication = 0
        has_weak_areas = False

        for answer in answers:
            # confidence_score stores technical_accuracy, communication_score stores communication
            accuracy = answer.get("confidence_score") or 50
            communication = answer.get("communication_score") or 50
            # Estimate completeness as average of accuracy and communication
            completeness = (accuracy + communication) // 2

            weak_areas = []
            if accuracy < 50:
                weak_areas.append("technical_accuracy")
                has_weak_areas = True
            if completeness < 50:
                weak_areas.append("completeness")
                has_weak_areas = True

            evaluations.append({
                "question_index": answer.get("question_index", 0),
                "question_text": answer.get("question_text", ""),
                "transcript": answer.get("transcript"),
                "scores": {
                    "technical_accuracy": accuracy,
                    "completeness": completeness,
                    "communication": communication,
                },
                "feedback": None,
                "weak_areas": weak_areas,
            })

            total_accuracy += accuracy
            total_completeness += completeness
            total_communication += communication

        num_answers = len(evaluations)
        avg_scores = {
            "technical_accuracy": total_accuracy // num_answers if num_answers else 0,
            "completeness": total_completeness // num_answers if num_answers else 0,
            "communication": total_communication // num_answers if num_answers else 0,
        }

        topic = session.get("topic", "General")
        difficulty = session.get("difficulty", "intermediate")

        # Determine total questions from session (use a reasonable default)
        total_questions = session.get("num_questions", num_answers)

        return {
            "session_id": str(session_id),
            "topic": topic,
            "difficulty": difficulty,
            "total_questions": total_questions,
            "answered_questions": num_answers,
            "evaluations": evaluations,
            "average_scores": avg_scores,
            "needs_follow_up": has_weak_areas,
        }

    async def generate_follow_up(
        self,
        user_id: str,
        session_id: UUID,
        question_index: int,
        weak_area: str,
    ) -> dict:
        """Generate a follow-up question targeting a weak area.

        Requirement 5.3: Generate follow-up question probing the weak area
        when an incomplete or incorrect answer is identified.

        Args:
            user_id: The authenticated user's ID.
            session_id: The session UUID.
            question_index: Index of the question with weak answer.
            weak_area: Description of the weak area to probe.

        Returns:
            Dict with generated follow-up question and reason.

        Raises:
            TechnicalSessionNotFoundError: If session not found or access denied.
            TechnicalSessionServiceError: If follow-up generation fails.
        """
        logger.info(
            "Generating follow-up: session=%s, question_index=%d, weak_area=%s",
            session_id,
            question_index,
            weak_area,
        )

        session = self._repository.get_session(session_id, user_id)
        if not session:
            raise TechnicalSessionNotFoundError(
                f"Session {session_id} not found or access denied"
            )

        if session.get("interview_type") != InterviewType.TECHNICAL.value:
            raise TechnicalSessionServiceError(
                "Session is not a technical interview session"
            )

        topic = session.get("topic", "General")
        difficulty = session.get("difficulty", "intermediate")

        # Get the original question context
        answers = self._repository.get_session_answers(session_id, user_id)
        original_question = ""
        original_answer = ""
        for answer in answers:
            if answer.get("question_index") == question_index:
                original_question = answer.get("question_text", "")
                original_answer = answer.get("transcript", "")
                break

        # Generate follow-up using Gemini
        follow_up = await self._generate_follow_up_question(
            topic=topic,
            difficulty=difficulty,
            original_question=original_question,
            original_answer=original_answer,
            weak_area=weak_area,
        )

        return {
            "question": follow_up["question"],
            "reason": follow_up["reason"],
            "original_question_index": question_index,
            "weak_area": weak_area,
        }

    async def _evaluate_technical_answer(
        self,
        question_text: str,
        answer_text: str,
        topic: str,
        difficulty: str,
    ) -> dict:
        """Evaluate a technical answer using Gemini for accuracy, completeness, communication.

        Args:
            question_text: The question that was asked.
            answer_text: The transcribed answer text.
            topic: Technical topic of the session.
            difficulty: Difficulty level of the session.

        Returns:
            Dict with scores, feedback, and weak_areas.
        """
        prompt = (
            f"You are an expert technical interviewer evaluating an answer on {topic} "
            f"at {difficulty} difficulty level.\n\n"
            f"Question: {question_text}\n\n"
            f"Candidate's Answer: {answer_text}\n\n"
            f"Evaluate this answer and return a JSON object with:\n"
            f'- "technical_accuracy": integer 0-100 (how technically correct is the answer)\n'
            f'- "completeness": integer 0-100 (how complete and thorough is the answer)\n'
            f'- "communication": integer 0-100 (how clearly is the answer communicated)\n'
            f'- "feedback": string (brief constructive feedback, 1-2 sentences)\n'
            f'- "weak_areas": array of strings (specific areas needing improvement, empty if good)\n\n'
            f"Return ONLY the JSON object, no other text or markdown formatting."
        )

        try:
            response_text = await asyncio.wait_for(
                self._gemini._call_gemini(prompt),
                timeout=EVALUATION_TIMEOUT,
            )
            return self._parse_evaluation_response(response_text)
        except (GeminiClientError, asyncio.TimeoutError, Exception) as e:
            logger.warning(
                "Gemini evaluation failed, using fallback scores: %s", str(e)
            )
            return self._fallback_evaluation(answer_text)

    def _parse_evaluation_response(self, response_text: str) -> dict:
        """Parse Gemini's evaluation response.

        Args:
            response_text: Raw response from Gemini.

        Returns:
            Parsed evaluation dict.
        """
        text = response_text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines)

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            logger.warning("Failed to parse evaluation JSON, using fallback")
            return self._fallback_evaluation("")

        scores = {
            "technical_accuracy": max(0, min(100, int(data.get("technical_accuracy", 50)))),
            "completeness": max(0, min(100, int(data.get("completeness", 50)))),
            "communication": max(0, min(100, int(data.get("communication", 50)))),
        }

        feedback = data.get("feedback", "Answer evaluated successfully.")
        weak_areas = data.get("weak_areas", [])

        if not isinstance(weak_areas, list):
            weak_areas = []

        # Auto-detect weak areas based on scores
        if scores["technical_accuracy"] < 50 and "technical_accuracy" not in weak_areas:
            weak_areas.append("technical_accuracy")
        if scores["completeness"] < 50 and "completeness" not in weak_areas:
            weak_areas.append("completeness")

        return {
            "scores": scores,
            "feedback": feedback,
            "weak_areas": weak_areas,
        }

    def _fallback_evaluation(self, answer_text: str) -> dict:
        """Generate a fallback evaluation when Gemini is unavailable.

        Uses basic heuristics based on answer length and content.

        Args:
            answer_text: The transcribed answer text.

        Returns:
            Fallback evaluation dict.
        """
        word_count = len(answer_text.split()) if answer_text else 0

        # Basic heuristics
        if word_count > 100:
            accuracy = 60
            completeness = 65
            communication = 60
        elif word_count > 50:
            accuracy = 50
            completeness = 50
            communication = 55
        elif word_count > 20:
            accuracy = 40
            completeness = 35
            communication = 45
        else:
            accuracy = 30
            completeness = 25
            communication = 35

        weak_areas = []
        if accuracy < 50:
            weak_areas.append("technical_accuracy")
        if completeness < 50:
            weak_areas.append("completeness")

        return {
            "scores": {
                "technical_accuracy": accuracy,
                "completeness": completeness,
                "communication": communication,
            },
            "feedback": "Evaluation performed using fallback analysis. "
            "AI evaluation was temporarily unavailable.",
            "weak_areas": weak_areas,
        }

    async def _generate_follow_up_question(
        self,
        topic: str,
        difficulty: str,
        original_question: str,
        original_answer: str,
        weak_area: str,
    ) -> dict:
        """Generate a follow-up question using Gemini targeting the weak area.

        Args:
            topic: Technical topic.
            difficulty: Difficulty level.
            original_question: The original question text.
            original_answer: The candidate's original answer.
            weak_area: The weak area to probe further.

        Returns:
            Dict with question and reason.

        Raises:
            TechnicalSessionServiceError: If generation fails.
        """
        prompt = (
            f"You are a technical interviewer conducting a {topic} interview at "
            f"{difficulty} difficulty level.\n\n"
            f"The candidate was asked: {original_question}\n\n"
            f"Their answer was: {original_answer}\n\n"
            f"The weak area identified is: {weak_area}\n\n"
            f"Generate a follow-up question that probes deeper into this weak area "
            f"to help assess the candidate's understanding.\n\n"
            f"Return a JSON object with:\n"
            f'- "text": the follow-up question text\n'
            f'- "topic": the topic category (string)\n'
            f'- "difficulty": difficulty level (string)\n'
            f'- "reason": why this follow-up was generated (1 sentence)\n\n'
            f"Return ONLY the JSON object, no other text or markdown formatting."
        )

        try:
            response_text = await asyncio.wait_for(
                self._gemini._call_gemini(prompt),
                timeout=EVALUATION_TIMEOUT,
            )
            return self._parse_follow_up_response(response_text, topic, difficulty, weak_area)
        except (GeminiClientError, asyncio.TimeoutError, Exception) as e:
            logger.warning("Gemini follow-up generation failed: %s", str(e))
            # Provide a reasonable fallback follow-up
            return {
                "question": {
                    "text": f"Can you explain more about {weak_area} in the context of {topic}?",
                    "topic": topic,
                    "difficulty": difficulty,
                    "interview_type": "technical",
                    "follow_up": None,
                },
                "reason": f"Follow-up generated to probe deeper into {weak_area}.",
            }

    def _parse_follow_up_response(
        self,
        response_text: str,
        topic: str,
        difficulty: str,
        weak_area: str,
    ) -> dict:
        """Parse Gemini's follow-up question response.

        Args:
            response_text: Raw response from Gemini.
            topic: Fallback topic value.
            difficulty: Fallback difficulty value.
            weak_area: The weak area being probed.

        Returns:
            Parsed follow-up dict with question and reason.
        """
        text = response_text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines)

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return {
                "question": {
                    "text": f"Can you elaborate further on {weak_area} as it relates to {topic}?",
                    "topic": topic,
                    "difficulty": difficulty,
                    "interview_type": "technical",
                    "follow_up": None,
                },
                "reason": f"Follow-up generated to assess understanding of {weak_area}.",
            }

        question_data = {
            "text": data.get("text", f"Tell me more about {weak_area} in {topic}."),
            "topic": data.get("topic", topic),
            "difficulty": data.get("difficulty", difficulty),
            "interview_type": "technical",
            "follow_up": None,
        }

        reason = data.get("reason", f"Follow-up targeting weak area: {weak_area}.")

        return {
            "question": question_data,
            "reason": reason,
        }
