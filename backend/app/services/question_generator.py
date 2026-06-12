"""Question generator service with cache layer and fallback mechanism.

Orchestrates question generation through three layers:
1. Cache check (fastest, no API call)
2. Gemini API (AI-generated, high quality)
3. Question bank fallback (predefined, ensures session continuity)

Resume-based questions bypass caching and have no fallback.

Requirements: 4.1, 5.1, 10.4, 17.3
"""

import logging
from typing import Optional

from app.integrations.gemini_client import GeminiClient, GeminiClientError
from app.models.question import Question, QuestionGenerationResult
from app.services.question_bank_service import QuestionBankService
from app.services.question_cache_service import QuestionCacheService

logger = logging.getLogger(__name__)


class QuestionGenerator:
    """Generates interview questions with caching and graceful fallback.

    Flow for non-resume questions:
    1. Check cache for existing questions matching parameters
    2. On cache hit: return cached questions immediately
    3. On cache miss: call Gemini API for generation
    4. On Gemini success: store in cache, return questions
    5. On Gemini failure: fall back to predefined question bank
    6. Log failures for monitoring

    Flow for resume-based questions:
    1. Call Gemini API directly (no cache, no fallback)
    2. On failure: raise error (resume questions are AI-generated only)
    """

    def __init__(
        self,
        cache_service: Optional[QuestionCacheService] = None,
        gemini_client: Optional[GeminiClient] = None,
        question_bank: Optional[QuestionBankService] = None,
    ) -> None:
        """Initialize the question generator with its dependencies.

        Args:
            cache_service: Question cache service instance. Creates default if None.
            gemini_client: Gemini API client instance. Creates default if None.
            question_bank: Question bank service instance. Creates default if None.
        """
        self._cache = cache_service or QuestionCacheService()
        self._gemini = gemini_client or GeminiClient()
        self._question_bank = question_bank or QuestionBankService()

    async def generate_questions(
        self,
        interview_type: str,
        role: str,
        topic: Optional[str] = None,
        difficulty: Optional[str] = None,
        num_questions: int = 5,
        resume_data: Optional[dict] = None,
    ) -> QuestionGenerationResult:
        """Generate interview questions with cache and fallback.

        Uses cache for non-resume requests; falls back to Gemini API on
        cache miss. If Gemini fails, uses predefined question bank.

        Resume-based questions are AI-generated only with no cache or fallback.

        Args:
            interview_type: Type of interview (hr, technical, behavioral, custom, resume_based).
            role: Target job role.
            topic: Optional specific topic for technical interviews.
            difficulty: Optional difficulty level (beginner, intermediate, advanced).
            resume_data: Optional resume data for personalized questions.
            num_questions: Number of questions to generate.

        Returns:
            QuestionGenerationResult with questions and metadata about source.

        Raises:
            GeminiClientError: Only for resume-based questions when Gemini fails
                (no fallback available for personalized questions).
        """
        # Resume-based questions: AI-only, no cache, no fallback
        if resume_data is not None:
            return await self._generate_resume_questions(
                resume_data, role, num_questions
            )

        # Standard questions: cache → Gemini → fallback
        return await self._generate_standard_questions(
            interview_type, role, topic, difficulty, num_questions
        )

    async def _generate_resume_questions(
        self,
        resume_data: dict,
        role: str,
        num_questions: int,
    ) -> QuestionGenerationResult:
        """Generate resume-based questions (AI-only, no fallback).

        Args:
            resume_data: Extracted resume data.
            role: Target job role.
            num_questions: Number of questions to generate.

        Returns:
            QuestionGenerationResult with AI-generated personalized questions.

        Raises:
            GeminiClientError: If Gemini API fails (no fallback for resume questions).
        """
        logger.info("Generating resume-based questions for role: %s", role)

        try:
            questions = await self._gemini.generate_resume_questions(
                resume_data=resume_data,
                role=role,
                num_questions=num_questions,
            )
            return QuestionGenerationResult(
                questions=questions,
                fallback_used=False,
                source="gemini",
            )
        except GeminiClientError:
            logger.error(
                "Gemini API failed for resume-based questions (role=%s). "
                "No fallback available for personalized questions.",
                role,
            )
            raise

    async def _generate_standard_questions(
        self,
        interview_type: str,
        role: str,
        topic: Optional[str],
        difficulty: Optional[str],
        num_questions: int,
    ) -> QuestionGenerationResult:
        """Generate standard questions with cache → Gemini → fallback flow.

        Args:
            interview_type: Type of interview.
            role: Target job role.
            topic: Optional topic.
            difficulty: Optional difficulty level.
            num_questions: Number of questions to generate.

        Returns:
            QuestionGenerationResult with questions and source metadata.
        """
        # Step 1: Check cache
        cached_questions = await self._cache.get_cached_questions(
            interview_type=interview_type,
            role=role,
            topic=topic,
            difficulty=difficulty,
        )

        if cached_questions:
            logger.info(
                "Cache hit: returning %d cached questions for type=%s, role=%s",
                len(cached_questions),
                interview_type,
                role,
            )
            return QuestionGenerationResult(
                questions=cached_questions,
                fallback_used=False,
                source="cache",
            )

        # Step 2: Try Gemini API
        try:
            questions = await self._gemini.generate_questions(
                interview_type=interview_type,
                role=role,
                topic=topic,
                difficulty=difficulty,
                num_questions=num_questions,
            )

            # Store in cache for future requests
            await self._cache.cache_questions(
                interview_type=interview_type,
                role=role,
                questions=questions,
                topic=topic,
                difficulty=difficulty,
            )

            logger.info(
                "Gemini generated %d questions for type=%s, role=%s, topic=%s",
                len(questions),
                interview_type,
                role,
                topic,
            )

            return QuestionGenerationResult(
                questions=questions,
                fallback_used=False,
                source="gemini",
            )

        except GeminiClientError as e:
            # Step 3: Fall back to predefined question bank
            logger.warning(
                "Gemini API failed, falling back to question bank: %s", str(e)
            )
            return self._fallback_to_question_bank(
                interview_type, role, topic, difficulty, num_questions
            )

    def _fallback_to_question_bank(
        self,
        interview_type: str,
        role: str,
        topic: Optional[str],
        difficulty: Optional[str],
        num_questions: int,
    ) -> QuestionGenerationResult:
        """Fall back to the predefined question bank.

        Logs the fallback event for monitoring and returns predefined questions.

        Args:
            interview_type: Type of interview.
            role: Target job role.
            topic: Optional topic.
            difficulty: Optional difficulty level.
            num_questions: Number of questions to return.

        Returns:
            QuestionGenerationResult with fallback_used=True flag.
        """
        logger.info(
            "Using fallback question bank for type=%s, role=%s, topic=%s, difficulty=%s",
            interview_type,
            role,
            topic,
            difficulty,
        )

        questions = self._question_bank.get_questions(
            interview_type=interview_type,
            role=role,
            topic=topic,
            difficulty=difficulty,
            num_questions=num_questions,
        )

        return QuestionGenerationResult(
            questions=questions,
            fallback_used=True,
            source="fallback",
        )

    async def invalidate_cache(self, pattern: Optional[str] = None) -> None:
        """Invalidate question cache entries.

        Args:
            pattern: Optional pattern to match cache keys.
                     If None, clears entire cache.
        """
        await self._cache.invalidate_cache(pattern)
