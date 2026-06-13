"""Groq Speech-to-Text client for audio transcription.

Provides a resilient interface to Groq's Whisper-based Speech-to-Text API
for converting audio recordings to text. Implements 1 retry with exponential
backoff and a 30-second timeout per request.

Requirements: 4.3 (transcription within 30 seconds), 17.3 (retry once on failure)
"""

import asyncio
import logging
from typing import Optional

from groq import AsyncGroq, APIError, APITimeoutError, RateLimitError, AuthenticationError

from app.config import get_settings

logger = logging.getLogger(__name__)

# Timeout for each Groq API call (seconds) - Requirement 4.3
REQUEST_TIMEOUT = 30.0

# Retry configuration - Requirement 17.3
MAX_RETRIES = 1
BASE_BACKOFF_SECONDS = 2.0

# Groq speech-to-text model
GROQ_STT_MODEL = "whisper-large-v3-turbo"


class GroqClientError(Exception):
    """Raised when Groq API call fails after all retries."""

    def __init__(self, message: str, is_retryable: bool = True) -> None:
        """Initialize with message and retryable flag.

        Args:
            message: Error description.
            is_retryable: Whether the error is transient and may succeed on retry.
        """
        super().__init__(message)
        self.is_retryable = is_retryable


class GroqClient:
    """Client for Groq Speech-to-Text API with retry and timeout logic.

    Implements:
    - 1 retry with exponential backoff on transient failures (Req 17.3)
    - 30-second timeout per request (Req 4.3)
    - Structured logging of failures for monitoring
    - Graceful handling of invalid API key, rate limits, network failures,
      timeouts, and invalid audio files
    """

    def __init__(self) -> None:
        """Initialize the Groq client with API key from settings."""
        settings = get_settings()
        self._api_key = settings.groq_api_key
        self._client: Optional[AsyncGroq] = None

    def _get_client(self) -> AsyncGroq:
        """Get or create the AsyncGroq client instance.

        Returns:
            Configured AsyncGroq client.

        Raises:
            GroqClientError: If API key is not configured.
        """
        if self._client is None:
            if not self._api_key:
                raise GroqClientError(
                    "Groq API key is not configured. Set GROQ_API_KEY in environment.",
                    is_retryable=False,
                )
            self._client = AsyncGroq(
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
        """Transcribe audio data to text via Groq Speech-to-Text with retry logic.

        Implements 1 retry with exponential backoff for transient errors.
        Enforces a 30-second timeout per request as required by Requirement 4.3.
        Non-retryable errors (invalid API key, invalid audio) fail immediately.

        Args:
            audio_data: Raw audio bytes to transcribe.
            filename: Filename hint for the audio format (e.g., "audio.webm").
            language: Optional language code (e.g., "en") to improve accuracy.

        Returns:
            Transcribed text string.

        Raises:
            GroqClientError: If transcription fails after all retries.
        """
        if not audio_data:
            raise GroqClientError(
                "No audio data provided for transcription",
                is_retryable=False,
            )

        last_error: Optional[Exception] = None

        for attempt in range(MAX_RETRIES + 1):
            try:
                transcript = await self._call_groq(audio_data, filename, language)
                return transcript
            except GroqClientError as e:
                last_error = e
                # Don't retry non-retryable errors (auth, invalid audio)
                if not e.is_retryable:
                    logger.error("Groq API non-retryable error: %s", str(e))
                    raise
                if attempt < MAX_RETRIES:
                    backoff = BASE_BACKOFF_SECONDS * (2**attempt)
                    logger.warning(
                        "Groq API call failed (attempt %d/%d), retrying in %.1fs: %s",
                        attempt + 1,
                        MAX_RETRIES + 1,
                        backoff,
                        str(e),
                    )
                    await asyncio.sleep(backoff)
                else:
                    logger.error(
                        "Groq API call failed after %d attempts: %s",
                        MAX_RETRIES + 1,
                        str(e),
                    )
            except asyncio.TimeoutError as e:
                last_error = e
                if attempt < MAX_RETRIES:
                    backoff = BASE_BACKOFF_SECONDS * (2**attempt)
                    logger.warning(
                        "Groq API timed out (attempt %d/%d), retrying in %.1fs",
                        attempt + 1,
                        MAX_RETRIES + 1,
                        backoff,
                    )
                    await asyncio.sleep(backoff)
                else:
                    logger.error(
                        "Groq API timed out after %d attempts",
                        MAX_RETRIES + 1,
                    )

        raise GroqClientError(
            f"Groq Speech-to-Text unavailable after {MAX_RETRIES + 1} attempts: {last_error}"
        )

    async def _call_groq(
        self,
        audio_data: bytes,
        filename: str,
        language: Optional[str],
    ) -> str:
        """Make a single transcription request to Groq API with timeout.

        Args:
            audio_data: Raw audio bytes.
            filename: Filename hint for audio format.
            language: Optional language code.

        Returns:
            Transcribed text.

        Raises:
            asyncio.TimeoutError: If the request exceeds the timeout.
            GroqClientError: If the API returns an error.
        """
        client = self._get_client()

        try:
            transcript = await asyncio.wait_for(
                self._send_transcription_request(client, audio_data, filename, language),
                timeout=REQUEST_TIMEOUT,
            )
            return transcript
        except asyncio.TimeoutError:
            logger.warning(
                "Groq API request timed out after %.0fs", REQUEST_TIMEOUT
            )
            raise
        except AuthenticationError as e:
            raise GroqClientError(
                f"Invalid Groq API key: {e}",
                is_retryable=False,
            ) from e
        except RateLimitError as e:
            raise GroqClientError(
                f"Groq API rate limit exceeded: {e}",
                is_retryable=True,
            ) from e
        except APITimeoutError as e:
            raise GroqClientError(
                f"Groq API timeout: {e}",
                is_retryable=True,
            ) from e
        except APIError as e:
            # Check for invalid audio (400 errors)
            status_code = getattr(e, "status_code", None)
            if status_code == 400:
                raise GroqClientError(
                    f"Invalid audio file or unsupported format: {e}",
                    is_retryable=False,
                ) from e
            raise GroqClientError(
                f"Groq API error: {e}",
                is_retryable=True,
            ) from e

    async def _send_transcription_request(
        self,
        client: AsyncGroq,
        audio_data: bytes,
        filename: str,
        language: Optional[str],
    ) -> str:
        """Send the actual transcription request to Groq.

        Args:
            client: AsyncGroq client instance.
            audio_data: Raw audio bytes.
            filename: Filename hint.
            language: Optional language code.

        Returns:
            Transcribed text from the response.
        """
        kwargs: dict = {
            "model": GROQ_STT_MODEL,
            "file": (filename, audio_data),
        }
        if language:
            kwargs["language"] = language

        response = await client.audio.transcriptions.create(**kwargs)
        return response.text
