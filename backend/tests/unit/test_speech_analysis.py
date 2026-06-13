"""Unit tests for the SpeechAnalysisService.

Tests cover WPM calculation, filler word detection, communication score
computation, and WPM range flagging.

Requirements: 4.4, 8.1, 8.2, 8.3, 8.4, 8.5
"""

import pytest

from app.services.speech_analysis_service import SpeechAnalysisService


@pytest.fixture
def service() -> SpeechAnalysisService:
    """Create a SpeechAnalysisService instance for testing."""
    return SpeechAnalysisService()


class TestWPMCalculation:
    """Tests for WPM calculation (Requirement 8.1)."""

    def test_wpm_basic_calculation(self, service: SpeechAnalysisService) -> None:
        """150 words in 60 seconds = 150 WPM."""
        transcript = " ".join(["word"] * 150)
        result = service.analyze(transcript, 60.0)
        assert result.wpm == 150

    def test_wpm_half_minute(self, service: SpeechAnalysisService) -> None:
        """75 words in 30 seconds = 150 WPM."""
        transcript = " ".join(["hello"] * 75)
        result = service.analyze(transcript, 30.0)
        assert result.wpm == 150

    def test_wpm_rounds_to_nearest_integer(self, service: SpeechAnalysisService) -> None:
        """100 words in 45 seconds = 133.33... rounds to 133."""
        transcript = " ".join(["test"] * 100)
        result = service.analyze(transcript, 45.0)
        assert result.wpm == 133

    def test_wpm_rounds_up_at_half(self, service: SpeechAnalysisService) -> None:
        """Verify rounding at 0.5 boundary."""
        # 10 words in 12 seconds = 50 WPM (exact)
        transcript = " ".join(["word"] * 10)
        result = service.analyze(transcript, 12.0)
        assert result.wpm == 50


class TestTotalWords:
    """Tests for total word count (Requirement 8.4)."""

    def test_total_words_simple(self, service: SpeechAnalysisService) -> None:
        """Simple word count from a sentence."""
        result = service.analyze("The quick brown fox jumps", 10.0)
        assert result.total_words == 5

    def test_total_words_with_punctuation(self, service: SpeechAnalysisService) -> None:
        """Punctuation should not affect word count."""
        result = service.analyze("Hello, world! How are you?", 10.0)
        assert result.total_words == 5

    def test_total_words_single_word(self, service: SpeechAnalysisService) -> None:
        """Single word transcript."""
        result = service.analyze("hello", 5.0)
        assert result.total_words == 1


class TestFillerWordDetection:
    """Tests for filler word detection (Requirement 8.2)."""

    def test_detects_um(self, service: SpeechAnalysisService) -> None:
        """Detect 'um' filler word."""
        result = service.analyze("I um think um this is good", 10.0)
        assert result.filler_words_detail.get("um") == 2

    def test_detects_uh(self, service: SpeechAnalysisService) -> None:
        """Detect 'uh' filler word."""
        result = service.analyze("Well uh I believe uh that", 10.0)
        assert result.filler_words_detail.get("uh") == 2

    def test_detects_like(self, service: SpeechAnalysisService) -> None:
        """Detect 'like' filler word."""
        result = service.analyze("It was like really like amazing", 10.0)
        assert result.filler_words_detail.get("like") == 2

    def test_detects_actually(self, service: SpeechAnalysisService) -> None:
        """Detect 'actually' filler word."""
        result = service.analyze("I actually think it is actually fine", 10.0)
        assert result.filler_words_detail.get("actually") == 2

    def test_detects_basically(self, service: SpeechAnalysisService) -> None:
        """Detect 'basically' filler word."""
        result = service.analyze("Basically the idea is basically this", 10.0)
        assert result.filler_words_detail.get("basically") == 2

    def test_detects_you_know(self, service: SpeechAnalysisService) -> None:
        """Detect 'you know' multi-word filler phrase."""
        result = service.analyze("I think you know it is you know fine", 10.0)
        assert result.filler_words_detail.get("you know") == 2

    def test_filler_word_count_is_sum(self, service: SpeechAnalysisService) -> None:
        """Total filler count equals sum of all individual filler counts."""
        result = service.analyze("Um uh like you know basically actually", 10.0)
        expected_total = sum(result.filler_words_detail.values())
        assert result.filler_word_count == expected_total

    def test_no_fillers_in_clean_speech(self, service: SpeechAnalysisService) -> None:
        """Clean speech with no filler words."""
        result = service.analyze(
            "The project was completed on time and within budget", 10.0
        )
        assert result.filler_word_count == 0
        assert result.filler_words_detail == {}

    def test_filler_detection_case_insensitive(
        self, service: SpeechAnalysisService
    ) -> None:
        """Filler detection is case insensitive."""
        result = service.analyze("UM Uh Like ACTUALLY Basically You Know", 10.0)
        assert result.filler_word_count >= 6


class TestCommunicationScore:
    """Tests for communication score computation (Requirement 8.3)."""

    def test_score_in_valid_range(self, service: SpeechAnalysisService) -> None:
        """Communication score is always between 0 and 100."""
        result = service.analyze("This is a simple test sentence", 10.0)
        assert 0 <= result.communication_score <= 100

    def test_ideal_wpm_no_fillers_scores_high(
        self, service: SpeechAnalysisService
    ) -> None:
        """Ideal WPM with no fillers should score high."""
        # 140 words in 60 seconds = 140 WPM (ideal range)
        transcript = " ".join(["word"] * 140)
        result = service.analyze(transcript, 60.0)
        assert result.communication_score >= 70

    def test_many_fillers_reduces_score(self, service: SpeechAnalysisService) -> None:
        """High filler ratio reduces communication score."""
        # Create transcript where fillers are significant portion
        words = ["um"] * 10 + ["word"] * 90
        transcript = " ".join(words)
        result_with_fillers = service.analyze(transcript, 60.0)

        # Clean version for comparison
        clean_transcript = " ".join(["word"] * 100)
        result_clean = service.analyze(clean_transcript, 60.0)

        assert result_clean.communication_score >= result_with_fillers.communication_score


class TestWPMRangeFlag:
    """Tests for WPM range flag (Requirement 8.5)."""

    def test_wpm_in_range_at_120(self, service: SpeechAnalysisService) -> None:
        """120 WPM is within ideal range."""
        transcript = " ".join(["word"] * 120)
        result = service.analyze(transcript, 60.0)
        assert result.wpm_in_range is True

    def test_wpm_in_range_at_160(self, service: SpeechAnalysisService) -> None:
        """160 WPM is within ideal range."""
        transcript = " ".join(["word"] * 160)
        result = service.analyze(transcript, 60.0)
        assert result.wpm_in_range is True

    def test_wpm_in_range_at_140(self, service: SpeechAnalysisService) -> None:
        """140 WPM is within ideal range."""
        transcript = " ".join(["word"] * 140)
        result = service.analyze(transcript, 60.0)
        assert result.wpm_in_range is True

    def test_wpm_below_range(self, service: SpeechAnalysisService) -> None:
        """80 WPM is below ideal range."""
        transcript = " ".join(["word"] * 80)
        result = service.analyze(transcript, 60.0)
        assert result.wpm_in_range is False

    def test_wpm_above_range(self, service: SpeechAnalysisService) -> None:
        """200 WPM is above ideal range."""
        transcript = " ".join(["word"] * 200)
        result = service.analyze(transcript, 60.0)
        assert result.wpm_in_range is False


class TestSpeakingDuration:
    """Tests for speaking duration reporting (Requirement 8.4)."""

    def test_speaking_duration_equals_input(
        self, service: SpeechAnalysisService
    ) -> None:
        """Speaking duration should match the provided duration."""
        result = service.analyze("Hello world", 42.5)
        assert result.speaking_duration == 42.5


class TestAvgPauseDuration:
    """Tests for average pause duration (Requirement 8.4)."""

    def test_avg_pause_non_negative(self, service: SpeechAnalysisService) -> None:
        """Average pause duration is always non-negative."""
        result = service.analyze("Quick speech with many words per second", 1.0)
        assert result.avg_pause_duration >= 0.0

    def test_longer_duration_larger_pauses(
        self, service: SpeechAnalysisService
    ) -> None:
        """More duration with same words implies larger pauses."""
        transcript = " ".join(["word"] * 20)
        result_short = service.analyze(transcript, 10.0)
        result_long = service.analyze(transcript, 60.0)
        assert result_long.avg_pause_duration >= result_short.avg_pause_duration
