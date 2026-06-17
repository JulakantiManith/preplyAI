"""Transcription service wrapping the Groq Speech-to-Text client.

Provides a service-layer interface for audio-to-text conversion,
including word-level timestamps for hesitation/pause detection.

Requirements: 4.3 (transcription within 30 seconds)
"""

import logging
from dataclasses import dataclass, field
from typing import Optional

from app.integrations.groq_client import GroqClient, GroqClientError, TranscriptionResult, WordTimestamp

logger = logging.getLogger(__name__)


class TranscriptionError(Exception):
    """Raised when transcription fails."""

    pass


@dataclass
class HesitationAnalysis:
    """Analysis of hesitations detected from word timing gaps."""

    hesitation_count: int = 0
    total_pause_duration: float = 0.0
    avg_pause_duration: float = 0.0
    long_pauses: list[float] = field(default_factory=list)  # Pauses > threshold


# Threshold for a gap between words to count as a hesitation/filler pause
HESITATION_PAUSE_THRESHOLD = 0.4  # seconds


class TranscriptionService:
    """Service for converting audio recordings to text with timing data.

    Returns transcription text plus word timestamps and hesitation analysis.
    """

    def __init__(self, groq_client: Optional[GroqClient] = None) -> None:
        self._client = groq_client or GroqClient()

    async def transcribe_audio(
        self,
        audio_data: bytes,
        filename: str = "audio.webm",
        language: Optional[str] = None,
    ) -> str:
        """Transcribe audio data to text (simple interface for backward compat).

        Args:
            audio_data: Raw audio bytes from recording.
            filename: Filename hint for audio format detection.
            language: Optional language code.

        Returns:
            Transcribed text string.

        Raises:
            TranscriptionError: If transcription fails after retries.
        """
        result = await self.transcribe_audio_detailed(audio_data, filename, language)
        return result.text

    async def transcribe_audio_detailed(
        self,
        audio_data: bytes,
        filename: str = "audio.webm",
        language: Optional[str] = None,
    ) -> TranscriptionResult:
        """Transcribe audio with full word timestamps.

        Args:
            audio_data: Raw audio bytes from recording.
            filename: Filename hint for audio format detection.
            language: Optional language code.

        Returns:
            TranscriptionResult with text, word timestamps, and duration.

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
            result = await self._client.transcribe(
                audio_data=audio_data,
                filename=filename,
                language=language,
            )
            logger.info(
                "Transcription completed: %d characters, %d words, %.1fs duration, %d word timestamps",
                len(result.text),
                len(result.text.split()),
                result.duration,
                len(result.words),
            )
            return result
        except GroqClientError as e:
            logger.error("Transcription failed: %s", str(e))
            raise TranscriptionError(f"Failed to transcribe audio: {e}") from e

    def analyze_hesitations(
        self,
        words: list[WordTimestamp],
        threshold: float = HESITATION_PAUSE_THRESHOLD,
    ) -> HesitationAnalysis:
        """Detect hesitations from gaps between word timestamps.

        A gap > threshold between consecutive words indicates a hesitation
        point where a filler word (um, uh) likely occurred but was stripped
        by the transcription model.

        Args:
            words: List of word timestamps from transcription.
            threshold: Minimum gap in seconds to count as hesitation.

        Returns:
            HesitationAnalysis with count and timing details.
        """
        if len(words) < 2:
            return HesitationAnalysis()

        hesitation_count = 0
        total_pause_duration = 0.0
        long_pauses: list[float] = []

        for i in range(1, len(words)):
            gap = words[i].start - words[i - 1].end
            if gap >= threshold:
                hesitation_count += 1
                total_pause_duration += gap
                long_pauses.append(gap)

        avg_pause = total_pause_duration / hesitation_count if hesitation_count > 0 else 0.0

        return HesitationAnalysis(
            hesitation_count=hesitation_count,
            total_pause_duration=total_pause_duration,
            avg_pause_duration=avg_pause,
            long_pauses=long_pauses,
        )
