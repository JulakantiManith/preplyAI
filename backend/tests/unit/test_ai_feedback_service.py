"""Unit tests for AI feedback service.

Tests algorithmic feedback generation and prompt construction logic.
"""

import pytest

from app.models.answer import SpeechMetrics
from app.models.feedback import FeedbackReport
from app.models.session import InterviewType
from app.services.ai_feedback_service import (
    AIFeedbackService,
    AnswerData,
    SessionData,
)


def _make_speech_metrics(**overrides) -> SpeechMetrics:
    """Create a SpeechMetrics instance with sensible defaults."""
    defaults = {
        "wpm": 140,
        "total_words": 200,
        "filler_word_count": 2,
        "filler_words_detail": {"um": 1, "uh": 1},
        "speaking_duration": 85.0,
        "avg_pause_duration": 0.4,
        "communication_score": 75,
        "wpm_in_range": True,
    }
    defaults.update(overrides)
    return SpeechMetrics(**defaults)


def _make_session_data(
    interview_type: InterviewType = InterviewType.HR,
    role: str = "Software Engineer",
    topic: str | None = None,
    difficulty: str | None = None,
) -> SessionData:
    """Create a SessionData instance with defaults."""
    return SessionData(
        interview_type=interview_type,
        role=role,
        topic=topic,
        difficulty=difficulty,
        answers=[
            AnswerData(
                question_text="Tell me about yourself.",
                transcript="I am a software engineer with 5 years of experience.",
                communication_score=75,
                confidence_score=65,
            ),
            AnswerData(
                question_text="What is your greatest strength?",
                transcript="My ability to solve complex problems systematically.",
                communication_score=80,
                confidence_score=70,
            ),
        ],
    )


class TestAlgorithmicFeedback:
    """Tests for the algorithmic fallback feedback generation."""

    def test_generates_minimum_strengths(self):
        """Feedback always contains at least 2 strengths."""
        service = AIFeedbackService(gemini_client=None)
        metrics = _make_speech_metrics()
        session_data = _make_session_data()

        report = service._generate_algorithmic_feedback(
            session_data, metrics, confidence_score=70
        )

        assert isinstance(report, FeedbackReport)
        assert len(report.strengths) >= 2

    def test_generates_minimum_weaknesses(self):
        """Feedback always contains at least 2 weaknesses."""
        service = AIFeedbackService(gemini_client=None)
        metrics = _make_speech_metrics()
        session_data = _make_session_data()

        report = service._generate_algorithmic_feedback(
            session_data, metrics, confidence_score=70
        )

        assert len(report.weaknesses) >= 2

    def test_generates_minimum_recommendations(self):
        """Feedback always contains at least 3 recommendations."""
        service = AIFeedbackService(gemini_client=None)
        metrics = _make_speech_metrics()
        session_data = _make_session_data()

        report = service._generate_algorithmic_feedback(
            session_data, metrics, confidence_score=70
        )

        assert len(report.recommendations) >= 3

    def test_confidence_recommendation_when_score_low(self):
        """When confidence score is 1-49, includes confidence recommendation."""
        service = AIFeedbackService(gemini_client=None)
        metrics = _make_speech_metrics()
        session_data = _make_session_data()

        report = service._generate_algorithmic_feedback(
            session_data, metrics, confidence_score=35
        )

        confidence_recs = [
            r for r in report.recommendations if "confidence" in r.lower()
        ]
        assert len(confidence_recs) >= 1

    def test_no_confidence_recommendation_when_score_high(self):
        """When confidence score is 50+, no forced confidence recommendation."""
        service = AIFeedbackService(gemini_client=None)
        metrics = _make_speech_metrics(
            wpm_in_range=True,
            communication_score=90,
            filler_word_count=0,
            avg_pause_duration=0.3,
        )
        session_data = _make_session_data()

        report = service._generate_algorithmic_feedback(
            session_data, metrics, confidence_score=80
        )

        # The first recommendation should NOT be about confidence
        confidence_recs = [
            r
            for r in report.recommendations
            if "confidence" in r.lower() and "project more confidence" in r.lower()
        ]
        assert len(confidence_recs) == 0

    def test_technical_interview_includes_technical_evaluation(self):
        """Technical interviews include technical_evaluation dict."""
        service = AIFeedbackService(gemini_client=None)
        metrics = _make_speech_metrics()
        session_data = _make_session_data(
            interview_type=InterviewType.TECHNICAL,
            topic="Data Structures",
            difficulty="intermediate",
        )

        report = service._generate_algorithmic_feedback(
            session_data, metrics, confidence_score=60
        )

        assert report.technical_evaluation is not None
        assert "accuracy" in report.technical_evaluation
        assert "completeness" in report.technical_evaluation
        assert "depth" in report.technical_evaluation
        assert "score" in report.technical_evaluation

    def test_non_technical_interview_no_technical_evaluation(self):
        """Non-technical interviews do not include technical_evaluation."""
        service = AIFeedbackService(gemini_client=None)
        metrics = _make_speech_metrics()
        session_data = _make_session_data(interview_type=InterviewType.HR)

        report = service._generate_algorithmic_feedback(
            session_data, metrics, confidence_score=60
        )

        assert report.technical_evaluation is None

    def test_slow_wpm_feedback(self):
        """Slow WPM results in appropriate weakness and recommendation."""
        service = AIFeedbackService(gemini_client=None)
        metrics = _make_speech_metrics(wpm=90, wpm_in_range=False)
        session_data = _make_session_data()

        report = service._generate_algorithmic_feedback(
            session_data, metrics, confidence_score=60
        )

        weakness_has_slow = any("slow" in w.lower() for w in report.weaknesses)
        assert weakness_has_slow

    def test_fast_wpm_feedback(self):
        """Fast WPM results in appropriate weakness."""
        service = AIFeedbackService(gemini_client=None)
        metrics = _make_speech_metrics(wpm=200, wpm_in_range=False)
        session_data = _make_session_data()

        report = service._generate_algorithmic_feedback(
            session_data, metrics, confidence_score=60
        )

        weakness_has_fast = any("fast" in w.lower() for w in report.weaknesses)
        assert weakness_has_fast

    def test_high_filler_word_feedback(self):
        """High filler word count results in weakness and recommendation."""
        service = AIFeedbackService(gemini_client=None)
        metrics = _make_speech_metrics(
            filler_word_count=15,
            filler_words_detail={"um": 8, "like": 5, "uh": 2},
            total_words=100,
        )
        session_data = _make_session_data()

        report = service._generate_algorithmic_feedback(
            session_data, metrics, confidence_score=60
        )

        filler_weakness = any("filler" in w.lower() for w in report.weaknesses)
        filler_rec = any("filler" in r.lower() for r in report.recommendations)
        assert filler_weakness
        assert filler_rec

    def test_behavioral_interview_recommendation(self):
        """Behavioral interview includes STAR method recommendation."""
        service = AIFeedbackService(gemini_client=None)
        metrics = _make_speech_metrics()
        session_data = _make_session_data(interview_type=InterviewType.BEHAVIORAL)

        report = service._generate_algorithmic_feedback(
            session_data, metrics, confidence_score=60
        )

        star_rec = any("STAR" in r for r in report.recommendations)
        assert star_rec


class TestPromptConstruction:
    """Tests for prompt construction logic."""

    def test_prompt_includes_interview_type(self):
        """Prompt includes the interview type."""
        service = AIFeedbackService(gemini_client=None)
        metrics = _make_speech_metrics()
        session_data = _make_session_data(interview_type=InterviewType.TECHNICAL)

        prompt = service._build_feedback_prompt(session_data, metrics, 65)

        assert "technical" in prompt.lower()

    def test_prompt_includes_role(self):
        """Prompt includes the target role."""
        service = AIFeedbackService(gemini_client=None)
        metrics = _make_speech_metrics()
        session_data = _make_session_data(role="Data Scientist")

        prompt = service._build_feedback_prompt(session_data, metrics, 65)

        assert "Data Scientist" in prompt

    def test_prompt_includes_topic_when_set(self):
        """Prompt includes topic when provided."""
        service = AIFeedbackService(gemini_client=None)
        metrics = _make_speech_metrics()
        session_data = _make_session_data(
            interview_type=InterviewType.TECHNICAL,
            topic="Machine Learning",
        )

        prompt = service._build_feedback_prompt(session_data, metrics, 65)

        assert "Machine Learning" in prompt

    def test_prompt_includes_confidence_instruction_when_low(self):
        """Prompt includes confidence instruction when score is 1-49."""
        service = AIFeedbackService(gemini_client=None)
        metrics = _make_speech_metrics()
        session_data = _make_session_data()

        prompt = service._build_feedback_prompt(session_data, metrics, 30)

        assert "confidence" in prompt.lower()
        assert "LOW" in prompt

    def test_prompt_no_confidence_instruction_when_high(self):
        """Prompt does not include forced confidence instruction when score >= 50."""
        service = AIFeedbackService(gemini_client=None)
        metrics = _make_speech_metrics()
        session_data = _make_session_data()

        prompt = service._build_feedback_prompt(session_data, metrics, 75)

        assert "LOW" not in prompt

    def test_prompt_includes_technical_evaluation_request(self):
        """Technical interviews request technical_evaluation in prompt."""
        service = AIFeedbackService(gemini_client=None)
        metrics = _make_speech_metrics()
        session_data = _make_session_data(interview_type=InterviewType.TECHNICAL)

        prompt = service._build_feedback_prompt(session_data, metrics, 65)

        assert "technical_evaluation" in prompt
        assert "accuracy" in prompt

    def test_prompt_includes_communication_structure_for_non_technical(self):
        """Non-technical interviews request communication structure evaluation."""
        service = AIFeedbackService(gemini_client=None)
        metrics = _make_speech_metrics()
        session_data = _make_session_data(interview_type=InterviewType.HR)

        prompt = service._build_feedback_prompt(session_data, metrics, 65)

        assert "communication structure" in prompt.lower()
        assert "logical flow" in prompt.lower()


class TestResponseParsing:
    """Tests for Gemini response parsing logic."""

    def test_parses_valid_json(self):
        """Parses a well-formed JSON response."""
        service = AIFeedbackService(gemini_client=None)
        session_data = _make_session_data()

        response = json.dumps({
            "strengths": ["Good pace", "Clear articulation"],
            "weaknesses": ["Some hesitation", "Could be more concise"],
            "recommendations": [
                "Practice more",
                "Use STAR method",
                "Reduce filler words",
            ],
        })

        report = service._parse_feedback_response(response, session_data, 70)

        assert len(report.strengths) == 2
        assert len(report.weaknesses) == 2
        assert len(report.recommendations) == 3

    def test_parses_json_with_code_fences(self):
        """Parses JSON wrapped in markdown code fences."""
        service = AIFeedbackService(gemini_client=None)
        session_data = _make_session_data()

        response = '```json\n' + json.dumps({
            "strengths": ["Good pace", "Clear articulation"],
            "weaknesses": ["Some hesitation", "Could be more concise"],
            "recommendations": [
                "Practice more",
                "Use STAR method",
                "Reduce filler words",
            ],
        }) + '\n```'

        report = service._parse_feedback_response(response, session_data, 70)

        assert len(report.strengths) == 2

    def test_adds_confidence_rec_when_missing(self):
        """Adds confidence recommendation if score 1-49 and none present."""
        service = AIFeedbackService(gemini_client=None)
        session_data = _make_session_data()

        response = json.dumps({
            "strengths": ["Good pace", "Clear articulation"],
            "weaknesses": ["Some hesitation", "Could be more concise"],
            "recommendations": [
                "Practice more",
                "Use STAR method",
                "Reduce filler words",
            ],
        })

        report = service._parse_feedback_response(response, session_data, 30)

        confidence_recs = [
            r for r in report.recommendations if "confidence" in r.lower()
        ]
        assert len(confidence_recs) >= 1

    def test_technical_interview_includes_evaluation(self):
        """Technical interview parse includes technical_evaluation."""
        service = AIFeedbackService(gemini_client=None)
        session_data = _make_session_data(interview_type=InterviewType.TECHNICAL)

        response = json.dumps({
            "strengths": ["Good knowledge", "Clear explanations"],
            "weaknesses": ["Missing edge cases", "Could go deeper"],
            "recommendations": [
                "Study more algorithms",
                "Practice whiteboarding",
                "Explain tradeoffs",
            ],
            "technical_evaluation": {
                "accuracy": "Good",
                "completeness": "Partial",
                "depth": "Surface level",
                "score": 72,
            },
        })

        report = service._parse_feedback_response(response, session_data, 65)

        assert report.technical_evaluation is not None
        assert report.technical_evaluation["score"] == 72

    def test_rejects_insufficient_strengths(self):
        """Raises error when strengths count is below minimum."""
        service = AIFeedbackService(gemini_client=None)
        session_data = _make_session_data()

        response = json.dumps({
            "strengths": ["Only one"],
            "weaknesses": ["A", "B"],
            "recommendations": ["A", "B", "C"],
        })

        with pytest.raises(Exception, match="Insufficient strengths"):
            service._parse_feedback_response(response, session_data, 70)

    def test_rejects_invalid_json(self):
        """Raises error on invalid JSON."""
        service = AIFeedbackService(gemini_client=None)
        session_data = _make_session_data()

        with pytest.raises(Exception, match="Failed to parse"):
            service._parse_feedback_response("not json at all", session_data, 70)


import json
