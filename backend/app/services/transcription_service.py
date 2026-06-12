"""Transcription service wrapping the Whisper client.

Provides a service-layer interface for audio-to-text conversion,
encapsulating the WhisperClient integration and adding logging.

Requirements: 4.3 (transcription within 30 seconds)
"""

import logging
from typing import Optional

from app.integrations.whisper_client import WhisperClient, WhisperClientError

logger = logging.getLogger(__name__)


class TranscriptionError(Exception):
    """Raised when transcription fails."""

    pass


class TranscriptionService:
    """Service for converting audio recordings to text.

    Wraps WhisperClient and provides a clean interface for the
    session service to call for transcription.
    """

    def __init__(self, whisper_client: Optional[WhisperClient] = None) -> None:
        """Initialize the transcription service.

        Args:
            whisper_client: WhisperClient instance. Creates default if None.
        """
        self._whisper = whisper_client or WhisperClient()

    async def transcribe_audio(
        self,
        audio_data: bytes,
        filename: str = "audio.webm",
        language: Optional[str] = None,
    ) -> str:
        """Transcribe audio data to text.

        Delegates to WhisperClient which handles retry logic and
        30-second timeout enforcement.

        Args:
            audio_data: Raw audio bytes from recording.
            filename: Filename hint for audio format detection.
            language: Optional language code for improved accuracy.

        Returns:
            Transcribed text string.

        Raises:
            TranscriptionError: If transcription fails after retries.
        """
        if not audio_data:
            raise TranscriptionError("No audio data provided")

        logger.info(
            "Starting transcription: file=%s, size=%d bytes",
            filename,
            len(audio_data),
        )

        try:
            transcript = await self._whisper.transcribe(
                audio_data=audio_data,
                filename=filename,
                language=language,
            )
            logger.info(
                "Transcription completed: %d characters, %d words",
                len(transcript),
                len(transcript.split()),
            )
            return transcript
        except WhisperClientError as e:
            logger.error("Transcription failed: %s", str(e))
            raise TranscriptionError(f"Failed to transcribe audio: {e}") from e
