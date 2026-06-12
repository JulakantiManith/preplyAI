"""Predefined question bank for fallback when Gemini API is unavailable.

Provides categorized question sets by interview type, topic, and difficulty.
Used as a fallback mechanism to ensure interview sessions continue without
interruption when the AI provider fails.

Resume-based questions have NO fallback (they are AI-generated only).

Requirements: 4.1, 5.1, 17.3
"""

import logging
import random
from typing import Optional

from app.models.question import Question
from app.services.question_bank_data import QUESTION_BANK

logger = logging.getLogger(__name__)


class QuestionBankService:
    """Service providing predefined fallback questions.

    Used when Gemini API is unavailable, rate limited, times out,
    or returns an error after retry. Ensures interview sessions
    continue without interruption.

    Note: Resume-based questions have NO fallback - they are
    AI-generated only.
    """

    def get_questions(
        self,
        interview_type: str,
        role: str,
        topic: Optional[str] = None,
        difficulty: Optional[str] = None,
        num_questions: int = 5,
    ) -> list[Question]:
        """Get predefined questions from the question bank.

        Selects questions based on interview type, topic, and difficulty.
        Falls back to more general categories if specific match not found.

        Args:
            interview_type: Type of interview (hr, technical, behavioral, custom).
            role: Target job role (used for context but not for bank lookup).
            topic: Optional topic for technical interviews.
            difficulty: Optional difficulty level.
            num_questions: Number of questions to return.

        Returns:
            List of Question objects from the predefined bank.
        """
        interview_type_lower = interview_type.lower().strip()
        topic_lower = (topic or "general").lower().strip()
        difficulty_lower = (difficulty or "intermediate").lower().strip()

        # Try exact match first
        questions_data = self._find_questions(
            interview_type_lower, topic_lower, difficulty_lower
        )

        if not questions_data:
            # Fall back to "general" topic
            questions_data = self._find_questions(
                interview_type_lower, "general", difficulty_lower
            )

        if not questions_data:
            # Fall back to "general" topic with "intermediate" difficulty
            questions_data = self._find_questions(
                interview_type_lower, "general", "intermediate"
            )

        if not questions_data:
            # Last resort: use HR general intermediate
            questions_data = self._find_questions("hr", "general", "intermediate")

        if not questions_data:
            logger.error(
                "Question bank is empty - no questions available for fallback"
            )
            return []

        # Randomly select questions without repetition
        selected = random.sample(
            questions_data, min(num_questions, len(questions_data))
        )

        questions = [
            Question(
                text=q["text"],
                topic=topic_lower if topic_lower != "general" else None,
                difficulty=difficulty_lower,
                interview_type=interview_type_lower,
                follow_up=q.get("follow_up"),
            )
            for q in selected
        ]

        logger.info(
            "Served %d fallback questions for type=%s, topic=%s, difficulty=%s",
            len(questions),
            interview_type_lower,
            topic_lower,
            difficulty_lower,
        )

        return questions

    def _find_questions(
        self, interview_type: str, topic: str, difficulty: str
    ) -> list[dict[str, str]]:
        """Look up questions in the bank by type, topic, and difficulty.

        Args:
            interview_type: Normalized interview type.
            topic: Normalized topic.
            difficulty: Normalized difficulty.

        Returns:
            List of question dicts or empty list if not found.
        """
        type_bank = QUESTION_BANK.get(interview_type, {})
        topic_bank = type_bank.get(topic, {})
        return topic_bank.get(difficulty, [])

    def get_available_topics(self, interview_type: str) -> list[str]:
        """Get available topics for a given interview type.

        Args:
            interview_type: Type of interview.

        Returns:
            List of available topic names.
        """
        type_bank = QUESTION_BANK.get(interview_type.lower().strip(), {})
        return list(type_bank.keys())

    def has_questions(
        self,
        interview_type: str,
        topic: Optional[str] = None,
        difficulty: Optional[str] = None,
    ) -> bool:
        """Check if the bank has questions for the given parameters.

        Args:
            interview_type: Type of interview.
            topic: Optional topic.
            difficulty: Optional difficulty.

        Returns:
            True if matching questions exist.
        """
        questions = self._find_questions(
            interview_type.lower().strip(),
            (topic or "general").lower().strip(),
            (difficulty or "intermediate").lower().strip(),
        )
        return len(questions) > 0
