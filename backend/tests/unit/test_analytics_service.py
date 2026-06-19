"""Unit tests for the analytics service."""

from unittest.mock import MagicMock, patch

import pytest

from app.models.analytics import AnalyticsOverview, ScoreTrend
from app.services.analytics_service import AnalyticsService


@pytest.fixture
def mock_repository():
    """Create a mock analytics repository."""
    with patch(
        "app.services.analytics_service.AnalyticsRepository"
    ) as MockRepo:
        mock_repo = MagicMock()
        MockRepo.return_value = mock_repo
        yield mock_repo


@pytest.fixture
def service(mock_repository):
    """Create an AnalyticsService with mocked repository."""
    return AnalyticsService()


class TestGetOverview:
    """Tests for AnalyticsService.get_overview."""

    def test_returns_has_sessions_false_when_no_sessions(
        self, service, mock_repository
    ):
        """When user has zero completed sessions, has_sessions is False."""
        mock_repository.get_completed_sessions_count_by_type.return_value = 0
        mock_repository.get_average_overall_score.return_value = None
        mock_repository.get_latest_session_scores.return_value = None
        mock_repository.get_sessions_for_date_range.return_value = []
        mock_repository.get_recent_sessions.return_value = []

        result = service.get_overview("user-123")

        assert result["has_sessions"] is False
        assert result["overview"].total_interview_sessions == 0
        assert result["overview"].total_presentation_sessions == 0
        assert result["overview"].average_overall_score is None
        assert result["weekly_progress"] == []
        assert result["recent_sessions"] == []

    def test_returns_has_sessions_true_with_sessions(
        self, service, mock_repository
    ):
        """When user has completed sessions, has_sessions is True."""
        mock_repository.get_completed_sessions_count_by_type.side_effect = [
            3,  # interview
            2,  # presentation
        ]
        mock_repository.get_average_overall_score.return_value = 75.5
        mock_repository.get_latest_session_scores.return_value = {
            "confidence_score": 80,
            "communication_score": 70,
        }
        mock_repository.get_sessions_for_date_range.return_value = []
        mock_repository.get_recent_sessions.return_value = [
            {
                "session_type": "interview",
                "created_at": "2024-01-15T10:00:00",
                "overall_score": 85,
            }
        ]

        result = service.get_overview("user-123")

        assert result["has_sessions"] is True
        assert result["overview"].total_interview_sessions == 3
        assert result["overview"].total_presentation_sessions == 2
        assert result["overview"].average_overall_score == 75.5
        assert result["overview"].latest_confidence_score == 80
        assert result["overview"].latest_communication_score == 70
        assert len(result["recent_sessions"]) == 1

    def test_weekly_progress_aggregates_by_day(
        self, service, mock_repository
    ):
        """Weekly progress groups sessions by date and computes averages."""
        mock_repository.get_completed_sessions_count_by_type.return_value = 0
        mock_repository.get_average_overall_score.return_value = None
        mock_repository.get_latest_session_scores.return_value = None
        mock_repository.get_sessions_for_date_range.return_value = [
            {"completed_at": "2024-01-15T10:00:00", "overall_score": 80},
            {"completed_at": "2024-01-15T14:00:00", "overall_score": 90},
            {"completed_at": "2024-01-16T09:00:00", "overall_score": 70},
        ]
        mock_repository.get_recent_sessions.return_value = []

        result = service.get_overview("user-123")

        weekly = result["weekly_progress"]
        assert len(weekly) == 2
        # First day: average of 80 and 90
        assert weekly[0].date == "2024-01-15"
        assert weekly[0].average_score == 85.0
        assert weekly[0].session_count == 2
        # Second day: only 70
        assert weekly[1].date == "2024-01-16"
        assert weekly[1].average_score == 70.0
        assert weekly[1].session_count == 1

    def test_latest_scores_none_when_no_sessions(
        self, service, mock_repository
    ):
        """When no sessions exist, latest scores are None."""
        mock_repository.get_completed_sessions_count_by_type.return_value = 0
        mock_repository.get_average_overall_score.return_value = None
        mock_repository.get_latest_session_scores.return_value = None
        mock_repository.get_sessions_for_date_range.return_value = []
        mock_repository.get_recent_sessions.return_value = []

        result = service.get_overview("user-123")

        assert result["overview"].latest_confidence_score is None
        assert result["overview"].latest_communication_score is None

    def test_recent_sessions_returns_up_to_five(
        self, service, mock_repository
    ):
        """Recent sessions calls repository with limit=5."""
        mock_repository.get_completed_sessions_count_by_type.return_value = 0
        mock_repository.get_average_overall_score.return_value = None
        mock_repository.get_latest_session_scores.return_value = None
        mock_repository.get_sessions_for_date_range.return_value = []
        mock_repository.get_recent_sessions.return_value = []

        service.get_overview("user-123")

        mock_repository.get_recent_sessions.assert_called_once_with(
            "user-123", limit=5
        )


class TestGetProgress:
    """Tests for AnalyticsService.get_progress."""

    def test_returns_empty_when_no_sessions_in_range(
        self, service, mock_repository
    ):
        """When no sessions exist in the time range, data_points is empty."""
        mock_repository.get_sessions_with_all_scores.return_value = []
        mock_repository.get_total_completed_sessions_count.return_value = 0

        result = service.get_progress("user-123", "weekly")

        assert result["has_sessions"] is False
        assert result["has_enough_data"] is False
        assert result["data_points"] == []

    def test_has_enough_data_true_when_three_or_more_sessions(
        self, service, mock_repository
    ):
        """has_enough_data is True when user has >= 3 total sessions."""
        mock_repository.get_sessions_with_all_scores.return_value = [
            {"completed_at": "2024-01-15T10:00:00", "overall_score": 80,
             "confidence_score": 70, "communication_score": 75},
            {"completed_at": "2024-01-16T10:00:00", "overall_score": 85,
             "confidence_score": 72, "communication_score": 78},
            {"completed_at": "2024-01-17T10:00:00", "overall_score": 90,
             "confidence_score": 75, "communication_score": 80},
        ]
        mock_repository.get_total_completed_sessions_count.return_value = 3

        result = service.get_progress("user-123", "weekly")

        assert result["has_sessions"] is True
        assert result["has_enough_data"] is True
        assert len(result["data_points"]) == 3

    def test_has_enough_data_false_when_fewer_than_three_sessions(
        self, service, mock_repository
    ):
        """has_enough_data is False when user has < 3 total sessions."""
        mock_repository.get_sessions_with_all_scores.return_value = [
            {"completed_at": "2024-01-15T10:00:00", "overall_score": 80,
             "confidence_score": 70, "communication_score": 75},
        ]
        mock_repository.get_total_completed_sessions_count.return_value = 1

        result = service.get_progress("user-123", "weekly")

        assert result["has_sessions"] is True
        assert result["has_enough_data"] is False

    def test_daily_bucketing_groups_by_date(
        self, service, mock_repository
    ):
        """Daily/weekly time range groups sessions by individual date."""
        mock_repository.get_sessions_with_all_scores.return_value = [
            {"completed_at": "2024-01-15T10:00:00", "overall_score": 80,
             "confidence_score": 70, "communication_score": 75},
            {"completed_at": "2024-01-15T14:00:00", "overall_score": 90,
             "confidence_score": 80, "communication_score": 85},
            {"completed_at": "2024-01-16T09:00:00", "overall_score": 70,
             "confidence_score": 60, "communication_score": 65},
        ]
        mock_repository.get_total_completed_sessions_count.return_value = 3

        result = service.get_progress("user-123", "weekly")

        data_points = result["data_points"]
        assert len(data_points) == 2
        assert data_points[0]["period"] == "2024-01-15"
        assert data_points[0]["session_count"] == 2
        assert data_points[0]["average_score"] == 85.0  # avg of 80 and 90
        assert data_points[1]["period"] == "2024-01-16"
        assert data_points[1]["session_count"] == 1
        assert data_points[1]["average_score"] == 70.0

    def test_handles_null_scores(self, service, mock_repository):
        """Sessions with null overall_score still count but don't affect average."""
        mock_repository.get_sessions_with_all_scores.return_value = [
            {"completed_at": "2024-01-15T10:00:00", "overall_score": 80,
             "confidence_score": 70, "communication_score": 75},
            {"completed_at": "2024-01-15T14:00:00", "overall_score": None,
             "confidence_score": None, "communication_score": None},
        ]
        mock_repository.get_total_completed_sessions_count.return_value = 2

        result = service.get_progress("user-123", "weekly")

        data_points = result["data_points"]
        assert len(data_points) == 1
        assert data_points[0]["session_count"] == 2
        assert data_points[0]["average_score"] == 80.0  # only one valid score


class TestGetTrends:
    """Tests for AnalyticsService.get_trends."""

    def test_returns_empty_trends_when_no_sessions(
        self, service, mock_repository
    ):
        """When no sessions exist, all trend series are empty."""
        mock_repository.get_sessions_with_all_scores.return_value = []
        mock_repository.get_total_completed_sessions_count.return_value = 0

        result = service.get_trends("user-123", "weekly")

        assert result["has_sessions"] is False
        assert result["has_enough_data"] is False
        assert result["trends"].overall_scores == []
        assert result["trends"].confidence_scores == []
        assert result["trends"].communication_scores == []

    def test_computes_independent_trends_per_score_type(
        self, service, mock_repository
    ):
        """Each score type has its own independent trend series."""
        mock_repository.get_sessions_with_all_scores.return_value = [
            {"completed_at": "2024-01-15T10:00:00", "overall_score": 80,
             "confidence_score": 70, "communication_score": 60},
            {"completed_at": "2024-01-15T14:00:00", "overall_score": 90,
             "confidence_score": 80, "communication_score": 70},
            {"completed_at": "2024-01-16T09:00:00", "overall_score": 75,
             "confidence_score": 65, "communication_score": 55},
        ]
        mock_repository.get_total_completed_sessions_count.return_value = 3

        result = service.get_trends("user-123", "weekly")

        trends = result["trends"]

        # Overall: day1 avg(80,90)=85, day2 avg(75)=75
        assert len(trends.overall_scores) == 2
        assert trends.overall_scores[0].date == "2024-01-15"
        assert trends.overall_scores[0].average_score == 85.0
        assert trends.overall_scores[1].date == "2024-01-16"
        assert trends.overall_scores[1].average_score == 75.0

        # Confidence: day1 avg(70,80)=75, day2 avg(65)=65
        assert len(trends.confidence_scores) == 2
        assert trends.confidence_scores[0].average_score == 75.0
        assert trends.confidence_scores[1].average_score == 65.0

        # Communication: day1 avg(60,70)=65, day2 avg(55)=55
        assert len(trends.communication_scores) == 2
        assert trends.communication_scores[0].average_score == 65.0
        assert trends.communication_scores[1].average_score == 55.0

    def test_handles_partial_null_scores(self, service, mock_repository):
        """Sessions with some null scores are excluded from those series only."""
        mock_repository.get_sessions_with_all_scores.return_value = [
            {"completed_at": "2024-01-15T10:00:00", "overall_score": 80,
             "confidence_score": None, "communication_score": 60},
            {"completed_at": "2024-01-15T14:00:00", "overall_score": 90,
             "confidence_score": 70, "communication_score": None},
        ]
        mock_repository.get_total_completed_sessions_count.return_value = 5

        result = service.get_trends("user-123", "weekly")

        trends = result["trends"]

        # Overall: both have scores, avg(80,90)=85
        assert len(trends.overall_scores) == 1
        assert trends.overall_scores[0].average_score == 85.0

        # Confidence: only second has score
        assert len(trends.confidence_scores) == 1
        assert trends.confidence_scores[0].average_score == 70.0

        # Communication: only first has score
        assert len(trends.communication_scores) == 1
        assert trends.communication_scores[0].average_score == 60.0

    def test_has_enough_data_reflects_total_sessions(
        self, service, mock_repository
    ):
        """has_enough_data uses total session count, not just filtered range."""
        mock_repository.get_sessions_with_all_scores.return_value = [
            {"completed_at": "2024-01-15T10:00:00", "overall_score": 80,
             "confidence_score": 70, "communication_score": 60},
        ]
        mock_repository.get_total_completed_sessions_count.return_value = 10

        result = service.get_trends("user-123", "daily")

        assert result["has_sessions"] is True
        assert result["has_enough_data"] is True
