"""Gemini API client with retry logic and timeout handling.

Provides a resilient interface to Google's Gemini API for generating
interview questions. Implements exponential backoff retry (1 retry)
with a 45-second timeout per request.

Requirements: 10.4 (feedback within 45s), 17.3 (retry once before failure)
"""

import asyncio
import json
import logging
from typing import Optional

import google.generativeai as genai
from google.api_core.exceptions import (
    GoogleAPIError,
    ResourceExhausted,
    ServiceUnavailable,
)

from app.config import get_settings
from app.models.question import Question

logger = logging.getLogger(__name__)

# Timeout for each Gemini API call (seconds)
REQUEST_TIMEOUT = 45.0

# Retry configuration
MAX_RETRIES = 1
BASE_BACKOFF_SECONDS = 2.0


class GeminiClientError(Exception):
    """Raised when Gemini API call fails after all retries."""

    pass


class GeminiClient:
    """Client for Google Gemini API with retry and timeout logic.

    Implements:
    - 1 retry with exponential backoff on failure
    - 45-second timeout per request
    - Structured logging of failures for monitoring
    """

    def __init__(self) -> None:
        """Initialize the Gemini client with API key from settings."""
        settings = get_settings()
        self._api_key = settings.gemini_api_key
        self._model_name = "gemini-1.5-flash"
        self._configured = False

    def _ensure_configured(self) -> None:
        """Configure the Gemini SDK if not already done."""
        if not self._configured and self._api_key:
            genai.configure(api_key=self._api_key)
            self._configured = True

    def _build_question_prompt(
        self,
        interview_type: str,
        role: str,
        topic: Optional[str] = None,
        difficulty: Optional[str] = None,
        num_questions: int = 5,
    ) -> str:
        """Build a structured prompt for question generation.

        Args:
            interview_type: Type of interview (hr, technical, behavioral, custom).
            role: Target job role.
            topic: Optional specific topic for technical interviews.
            difficulty: Optional difficulty level (beginner, intermediate, advanced).
            num_questions: Number of questions to generate.

        Returns:
            Formatted prompt string for Gemini.
        """
        prompt_parts = [
            f"Generate exactly {num_questions} interview questions for a {interview_type} interview.",
            f"Target role: {role}.",
        ]

        if topic:
            prompt_parts.append(f"Topic: {topic}.")
        if difficulty:
            prompt_parts.append(f"Difficulty level: {difficulty}.")

        prompt_parts.append(
            "\nReturn the questions as a JSON array of objects with the following fields:"
            '\n- "text": the question text (string, required)'
            '\n- "topic": topic category (string or null)'
            '\n- "difficulty": difficulty level (string or null)'
            '\n- "follow_up": a suggested follow-up question (string or null)'
            "\n\nReturn ONLY the JSON array, no other text or markdown formatting."
        )

        return " ".join(prompt_parts)

    def _build_resume_question_prompt(
        self,
        resume_data: dict,
        role: str,
        num_questions: int = 5,
    ) -> str:
        """Build a prompt for resume-based question generation.

        Args:
            resume_data: Extracted resume data (skills, projects, experience, education).
            role: Target job role.
            num_questions: Number of questions to generate.

        Returns:
            Formatted prompt string for Gemini.
        """
        resume_summary = json.dumps(resume_data, indent=2)

        return (
            f"Generate exactly {num_questions} personalized interview questions "
            f"based on the following resume data for a {role} position.\n\n"
            f"Resume data:\n{resume_summary}\n\n"
            "Focus on the candidate's specific experience, skills, and projects. "
            "Ask questions that probe deeper into their claimed expertise.\n\n"
            "Return the questions as a JSON array of objects with the following fields:\n"
            '- "text": the question text (string, required)\n'
            '- "topic": topic category (string or null)\n'
            '- "difficulty": difficulty level (string or null)\n'
            '- "follow_up": a suggested follow-up question (string or null)\n\n'
            "Return ONLY the JSON array, no other text or markdown formatting."
        )

    async def _call_gemini(self, prompt: str) -> str:
        """Make a single API call to Gemini with timeout.

        Args:
            prompt: The prompt to send to Gemini.

        Returns:
            Raw text response from Gemini.

        Raises:
            asyncio.TimeoutError: If the request exceeds 45 seconds.
            GeminiClientError: If the API returns an error.
        """
        self._ensure_configured()

        if not self._api_key:
            raise GeminiClientError("Gemini API key is not configured")

        model = genai.GenerativeModel(self._model_name)

        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(model.generate_content, prompt),
                timeout=REQUEST_TIMEOUT,
            )
            if response.text:
                return response.text
            raise GeminiClientError("Gemini returned empty response")
        except asyncio.TimeoutError:
            raise
        except (GoogleAPIError, ResourceExhausted, ServiceUnavailable) as e:
            raise GeminiClientError(f"Gemini API error: {e}") from e

    def _parse_questions_response(
        self,
        response_text: str,
        interview_type: str,
        topic: Optional[str],
        difficulty: Optional[str],
    ) -> list[Question]:
        """Parse Gemini's JSON response into Question objects.

        Args:
            response_text: Raw response text from Gemini.
            interview_type: Interview type for fallback field values.
            topic: Topic for fallback field values.
            difficulty: Difficulty for fallback field values.

        Returns:
            List of Question objects.

        Raises:
            GeminiClientError: If response cannot be parsed.
        """
        # Strip markdown code fences if present
        text = response_text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            # Remove first and last lines (code fences)
            lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines)

        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise GeminiClientError(
                f"Failed to parse Gemini response as JSON: {e}"
            ) from e

        if not isinstance(data, list):
            raise GeminiClientError("Gemini response is not a JSON array")

        questions: list[Question] = []
        for item in data:
            if isinstance(item, dict) and "text" in item:
                questions.append(
                    Question(
                        text=item["text"],
                        topic=item.get("topic", topic),
                        difficulty=item.get("difficulty", difficulty),
                        interview_type=interview_type,
                        follow_up=item.get("follow_up"),
                    )
                )

        if not questions:
            raise GeminiClientError("Gemini response contained no valid questions")

        return questions

    async def generate_questions(
        self,
        interview_type: str,
        role: str,
        topic: Optional[str] = None,
        difficulty: Optional[str] = None,
        num_questions: int = 5,
    ) -> list[Question]:
        """Generate interview questions via Gemini API with retry logic.

        Implements 1 retry with exponential backoff. Logs failures for monitoring.

        Args:
            interview_type: Type of interview (hr, technical, behavioral, custom).
            role: Target job role.
            topic: Optional specific topic.
            difficulty: Optional difficulty level.
            num_questions: Number of questions to generate.

        Returns:
            List of generated Question objects.

        Raises:
            GeminiClientError: If generation fails after all retries.
        """
        prompt = self._build_question_prompt(
            interview_type, role, topic, difficulty, num_questions
        )

        last_error: Optional[Exception] = None

        for attempt in range(MAX_RETRIES + 1):
            try:
                response_text = await self._call_gemini(prompt)
                return self._parse_questions_response(
                    response_text, interview_type, topic, difficulty
                )
            except (GeminiClientError, asyncio.TimeoutError) as e:
                last_error = e
                if attempt < MAX_RETRIES:
                    backoff = BASE_BACKOFF_SECONDS * (2**attempt)
                    logger.warning(
                        "Gemini API call failed (attempt %d/%d), retrying in %.1fs: %s",
                        attempt + 1,
                        MAX_RETRIES + 1,
                        backoff,
                        str(e),
                    )
                    await asyncio.sleep(backoff)
                else:
                    logger.error(
                        "Gemini API call failed after %d attempts: %s",
                        MAX_RETRIES + 1,
                        str(e),
                    )

        raise GeminiClientError(
            f"Gemini API unavailable after {MAX_RETRIES + 1} attempts: {last_error}"
        )

    async def generate_resume_questions(
        self,
        resume_data: dict,
        role: str,
        num_questions: int = 5,
    ) -> list[Question]:
        """Generate personalized questions based on resume data.

        Resume-based questions are AI-generated only with no fallback.
        Implements 1 retry with exponential backoff.

        Args:
            resume_data: Extracted resume data dict.
            role: Target job role.
            num_questions: Number of questions to generate.

        Returns:
            List of personalized Question objects.

        Raises:
            GeminiClientError: If generation fails after all retries.
        """
        prompt = self._build_resume_question_prompt(resume_data, role, num_questions)

        last_error: Optional[Exception] = None

        for attempt in range(MAX_RETRIES + 1):
            try:
                response_text = await self._call_gemini(prompt)
                return self._parse_questions_response(
                    response_text, "resume_based", None, None
                )
            except (GeminiClientError, asyncio.TimeoutError) as e:
                last_error = e
                if attempt < MAX_RETRIES:
                    backoff = BASE_BACKOFF_SECONDS * (2**attempt)
                    logger.warning(
                        "Gemini resume question generation failed (attempt %d/%d), "
                        "retrying in %.1fs: %s",
                        attempt + 1,
                        MAX_RETRIES + 1,
                        backoff,
                        str(e),
                    )
                    await asyncio.sleep(backoff)
                else:
                    logger.error(
                        "Gemini resume question generation failed after %d attempts: %s",
                        MAX_RETRIES + 1,
                        str(e),
                    )

        raise GeminiClientError(
            f"Gemini API unavailable for resume questions after "
            f"{MAX_RETRIES + 1} attempts: {last_error}"
        )
