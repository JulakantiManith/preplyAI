"""Whisper API client for audio transcription with retry and timeout.

Provides a resilient interface to OpenAI's Whisper API for converting
audio recordings to text. Implements 1 retry with exponential backoff
and a 30-second timeout per request.

Requirements: 4.3 (transcription within 30 seconds), 17.3 (retry once on failure)
"""

import asyncio
import logging
from typing import Optional

from openai import AsyncOpenAI, APIError, APITimeoutError, RateLimitError

from app.config import get_settings

logger = logging.getLogger(__name__)

# Timeout for each Whisper API call (seconds) - Requirement 4.3
REQUEST_TIMEOUT = 30.0

# Retry configuration - Requirement 17.3
MAX_RETRIES = 1
BASE_BACKOFF_SECONDS = 2.0


class WhisperClientError(Exception):
    """Raised when Whisper API call fails after all retries."""

    pass


class WhisperClient:
    """Client for OpenAI Whisper API with retry and timeout logic.

    Implements:
    - 1 retry with exponential backoff on failure (Req 17.3)
    - 30-second timeout per request (Req 4.3)
    - Structured logging of failures for monitoring
    """

    def __init__(self) -> None:
        """Initialize the Whisper client with API key from settings."""
        settings = get_settings()
        self._api_key = settings.whisper_api_key
        self._client: Optional[AsyncOpenAI] = None

    def _get_client(self) -> AsyncOpenAI:
        """Get or create the AsyncOpenAI client instance."""
        if self._client is None:
            if not self._api_key:
                raise WhisperClientError("Whisper API key is not configured")
            self._client = AsyncOpenAI(
                api_key=self._api_key,
                timeout=REQUEST_TIMEOUT,
            )
        return self._client

    async def transcribe(
        self,
        audio_data: bytes,
        filename: str = "audio.webm",
        language: Optional[str] = None,
    ) -> str:
        """Transcribe audio data to text via Whisper API with retry logic.

        Implements 1 retry with exponential backoff. Enforces a 30-second
        timeout per request as required by Requirement 4.3.

        Args:
            audio_data: Raw audio bytes to transcribe.
            filename: Filename hint for the audio format (e.g., "audio.webm").
            language: Optional language code (e.g., "en") to improve accuracy.

        Returns:
            Transcribed text string.

        Raises:
            WhisperClientError: If transcription fails after all retries.
        """
        if not audio_data:
            raise WhisperClientError("No audio data provided for transcription")

        last_error: Optional[Exception] = None

        for attempt in range(MAX_RETRIES + 1):
            try:
                transcript = await self._call_whisper(audio_data, filename, language)
                return transcript
            except (WhisperClientError, asyncio.TimeoutError) as e:
                last_error = e
                if attempt < MAX_RETRIES:
                    backoff = BASE_BACKOFF_SECONDS * (2**attempt)
                    logger.warning(
                        "Whisper API call failed (attempt %d/%d), retrying in %.1fs: %s",
                        attempt + 1,
                        MAX_RETRIES + 1,
                        backoff,
                        str(e),
                    )
                    await asyncio.sleep(backoff)
                else:
                    logger.error(
                        "Whisper API call failed after %d attempts: %s",
                        MAX_RETRIES + 1,
                        str(e),
                    )

        raise WhisperClientError(
            f"Whisper API unavailable after {MAX_RETRIES + 1} attempts: {last_error}"
        )

    async def _call_whisper(
        self,
        audio_data: bytes,
        filename: str,
        language: Optional[str],
    ) -> str:
        """Make a single transcription request to Whisper API with timeout.

        Args:
            audio_data: Raw audio bytes.
            filename: Filename hint for audio format.
            language: Optional language code.

        Returns:
            Transcribed text.

        Raises:
            asyncio.TimeoutError: If the request exceeds 30 seconds.
            WhisperClientError: If the API returns an error.
        """
        client = self._get_client()

        try:
            transcript = await asyncio.wait_for(
                self._send_transcription_request(client, audio_data, filename, language),
                timeout=REQUEST_TIMEOUT,
            )
            return transcript
        except asyncio.TimeoutError:
            logger.warning("Whisper API request timed out after %.0fs", REQUEST_TIMEOUT)
            raise
        except (APIError, APITimeoutError, RateLimitError) as e:
            raise WhisperClientError(f"Whisper API error: {e}") from e

    async def _send_transcription_request(
        self,
        client: AsyncOpenAI,
        audio_data: bytes,
        filename: str,
        language: Optional[str],
    ) -> str:
        """Send the actual transcription request to OpenAI.

        Args:
            client: AsyncOpenAI client instance.
            audio_data: Raw audio bytes.
            filename: Filename hint.
            language: Optional language code.

        Returns:
            Transcribed text from the response.
        """
        kwargs: dict = {
            "model": "whisper-1",
            "file": (filename, audio_data),
        }
        if language:
            kwargs["language"] = language

        response = await client.audio.transcriptions.create(**kwargs)
        return response.text
