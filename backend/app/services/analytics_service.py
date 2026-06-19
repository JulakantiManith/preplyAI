"""Analytics service for computing dashboard metrics.

Provides business logic for aggregating session data into
dashboard-ready analytics including overview metrics, weekly
progress chart data, recent sessions, progress data, and score trends.

Requirements: 3.1, 3.2, 3.3, 3.4, 11.1, 11.2, 11.3, 11.4, 11.5
"""

import logging
from datetime import UTC, datetime, timedelta

from app.models.analytics import AnalyticsOverview, AnalyticsTrends, ScoreTrend
from app.repositories.analytics_repository import AnalyticsRepository

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service layer for analytics and dashboard data."""

    def __init__(self) -> None:
        """Initialize with analytics repository."""
        self._repository = AnalyticsRepository()

    def get_overview(self, user_id: str, time_range: str = "weekly") -> dict:
        """Get the complete dashboard overview for a user.

        Computes aggregate metrics, progress chart data for the selected
        time range, and recent sessions list.

        Args:
            user_id: The authenticated user's ID.
            time_range: One of 'daily', 'weekly', 'monthly', '3months', 'yearly'.

        Returns:
            Dictionary containing:
              - has_sessions: bool indicating if user has any completed sessions
              - overview: AnalyticsOverview metrics
              - weekly_progress: list of ScoreTrend for selected time range
              - recent_sessions: list of recent session summaries
        """
        # Get session counts by type
        total_interview = self._repository.get_completed_sessions_count_by_type(
            user_id, "interview"
        )
        total_presentation = self._repository.get_completed_sessions_count_by_type(
            user_id, "presentation"
        )

        total_sessions = total_interview + total_presentation
        has_sessions = total_sessions > 0

        # Get average overall score
        average_score = self._repository.get_average_overall_score(user_id)

        # Get latest confidence and communication scores
        latest_scores = self._repository.get_latest_session_scores(user_id)
        latest_confidence = None
        latest_communication = None
        if latest_scores:
            latest_confidence = latest_scores.get("confidence_score")
            latest_communication = latest_scores.get("communication_score")

        overview = AnalyticsOverview(
            total_interview_sessions=total_interview,
            total_presentation_sessions=total_presentation,
            average_overall_score=average_score,
            latest_confidence_score=latest_confidence,
            latest_communication_score=latest_communication,
        )

        # Get weekly progress chart data
        weekly_progress = self._get_progress(user_id, time_range)

        # Get recent sessions
        recent_sessions = self._repository.get_recent_sessions(user_id, limit=5)

        return {
            "has_sessions": has_sessions,
            "overview": overview,
            "weekly_progress": weekly_progress,
            "recent_sessions": recent_sessions,
        }

    def _get_progress(self, user_id: str, time_range: str) -> list[ScoreTrend]:
        """Get score aggregates for the selected time range.

        Args:
            user_id: The authenticated user's ID.
            time_range: One of 'daily', 'weekly', 'monthly', '3months', 'yearly'.

        Returns:
            List of ScoreTrend objects for the selected period.
        """
        today = datetime.now(UTC).date()

        if time_range == "daily":
            # Today only
            start = today
            end = today
        elif time_range == "weekly":
            # Current week (Monday-Sunday)
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=6)
        elif time_range == "monthly":
            # Last 30 days
            start = today - timedelta(days=29)
            end = today
        elif time_range == "3months":
            # Last 90 days
            start = today - timedelta(days=89)
            end = today
        elif time_range == "yearly":
            # Last 365 days
            start = today - timedelta(days=364)
            end = today
        else:
            # Default to weekly
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=6)

        start_date = f"{start}T00:00:00"
        end_date = f"{end}T23:59:59"

        sessions = self._repository.get_sessions_for_date_range(
            user_id, start_date, end_date
        )

        if not sessions:
            return []

        # Group sessions by date and compute daily averages
        daily_data: dict[str, list[int]] = {}
        for session in sessions:
            completed_at = session.get("completed_at", "")
            score = session.get("overall_score")
            if not completed_at or score is None:
                continue

            # Extract date portion (YYYY-MM-DD)
            date_str = completed_at[:10]
            if date_str not in daily_data:
                daily_data[date_str] = []
            daily_data[date_str].append(score)

        # Build ScoreTrend list sorted by date
        trends = []
        for date_str in sorted(daily_data.keys()):
            scores = daily_data[date_str]
            avg_score = round(sum(scores) / len(scores), 1)
            trends.append(
                ScoreTrend(
                    date=date_str,
                    average_score=avg_score,
                    session_count=len(scores),
                )
            )

        return trends


    def _get_date_range(self, time_range: str) -> tuple:
        """Get start and end dates for the selected time range.

        Args:
            time_range: One of 'daily', 'weekly', 'monthly', '3months', 'yearly'.

        Returns:
            Tuple of (start_date, end_date) as date objects.
        """
        today = datetime.now(UTC).date()

        if time_range == "daily":
            start = today
            end = today
        elif time_range == "weekly":
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=6)
        elif time_range == "monthly":
            start = today - timedelta(days=29)
            end = today
        elif time_range == "3months":
            start = today - timedelta(days=89)
            end = today
        elif time_range == "yearly":
            start = today - timedelta(days=364)
            end = today
        else:
            # Default to weekly
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=6)

        return start, end

    def _get_bucket_key(self, date_str: str, time_range: str) -> str:
        """Get the bucket key for a given date based on time range.

        For daily/weekly time ranges, bucket by individual date.
        For monthly/3months/yearly, bucket by ISO week.

        Args:
            date_str: Date string in YYYY-MM-DD format.
            time_range: The selected time range.

        Returns:
            Bucket key string (date or week identifier).
        """
        from datetime import date as date_type

        parts = date_str.split("-")
        d = date_type(int(parts[0]), int(parts[1]), int(parts[2]))

        if time_range in ("daily", "weekly"):
            # Bucket by individual day
            return date_str
        elif time_range == "monthly":
            # Bucket by ISO week
            iso_year, iso_week, _ = d.isocalendar()
            return f"{iso_year}-W{iso_week:02d}"
        else:
            # For 3months and yearly, bucket by month
            return f"{d.year}-{d.month:02d}"

    def get_progress(self, user_id: str, time_range: str = "weekly") -> dict:
        """Get session frequency and average scores for progress display.

        Computes session counts and average overall scores bucketed by
        day/week/month depending on the time range.

        Args:
            user_id: The authenticated user's ID.
            time_range: One of 'daily', 'weekly', 'monthly', '3months', 'yearly'.

        Returns:
            Dictionary containing:
              - has_sessions: bool
              - has_enough_data: bool (true when >= 3 total sessions)
              - data_points: list of progress data points
        """
        start, end = self._get_date_range(time_range)
        start_date = f"{start}T00:00:00"
        end_date = f"{end}T23:59:59"

        sessions = self._repository.get_sessions_with_all_scores(
            user_id, start_date, end_date
        )
        total_sessions = self._repository.get_total_completed_sessions_count(user_id)

        has_sessions = total_sessions > 0
        has_enough_data = total_sessions >= 3

        if not sessions:
            return {
                "has_sessions": has_sessions,
                "has_enough_data": has_enough_data,
                "data_points": [],
            }

        # Group sessions by bucket
        buckets: dict[str, list[dict]] = {}
        for session in sessions:
            completed_at = session.get("completed_at", "")
            if not completed_at:
                continue
            date_str = completed_at[:10]
            bucket_key = self._get_bucket_key(date_str, time_range)
            if bucket_key not in buckets:
                buckets[bucket_key] = []
            buckets[bucket_key].append(session)

        # Build data points
        data_points = []
        for bucket_key in sorted(buckets.keys()):
            bucket_sessions = buckets[bucket_key]
            session_count = len(bucket_sessions)

            # Compute average overall score (skip None values)
            scores = [
                s["overall_score"]
                for s in bucket_sessions
                if s.get("overall_score") is not None
            ]
            average_score = round(sum(scores) / len(scores), 1) if scores else None

            data_points.append(
                {
                    "period": bucket_key,
                    "session_count": session_count,
                    "average_score": average_score,
                }
            )

        return {
            "has_sessions": has_sessions,
            "has_enough_data": has_enough_data,
            "data_points": data_points,
        }

    def get_trends(self, user_id: str, time_range: str = "weekly") -> dict:
        """Get score trend data for overall, confidence, and communication scores.

        Computes independent trend series for each score type, bucketed by
        day/week/month depending on the time range.

        Args:
            user_id: The authenticated user's ID.
            time_range: One of 'daily', 'weekly', 'monthly', '3months', 'yearly'.

        Returns:
            Dictionary containing:
              - has_sessions: bool
              - has_enough_data: bool (true when >= 3 total sessions)
              - trends: AnalyticsTrends with independent series
        """
        start, end = self._get_date_range(time_range)
        start_date = f"{start}T00:00:00"
        end_date = f"{end}T23:59:59"

        sessions = self._repository.get_sessions_with_all_scores(
            user_id, start_date, end_date
        )
        total_sessions = self._repository.get_total_completed_sessions_count(user_id)

        has_sessions = total_sessions > 0
        has_enough_data = total_sessions >= 3

        if not sessions:
            return {
                "has_sessions": has_sessions,
                "has_enough_data": has_enough_data,
                "trends": AnalyticsTrends(),
            }

        # Group sessions by bucket for each score type
        overall_buckets: dict[str, list[float]] = {}
        confidence_buckets: dict[str, list[float]] = {}
        communication_buckets: dict[str, list[float]] = {}
        session_counts: dict[str, int] = {}

        for session in sessions:
            completed_at = session.get("completed_at", "")
            if not completed_at:
                continue
            date_str = completed_at[:10]
            bucket_key = self._get_bucket_key(date_str, time_range)

            # Track session count per bucket
            session_counts[bucket_key] = session_counts.get(bucket_key, 0) + 1

            # Overall score
            overall = session.get("overall_score")
            if overall is not None:
                if bucket_key not in overall_buckets:
                    overall_buckets[bucket_key] = []
                overall_buckets[bucket_key].append(float(overall))

            # Confidence score
            confidence = session.get("confidence_score")
            if confidence is not None:
                if bucket_key not in confidence_buckets:
                    confidence_buckets[bucket_key] = []
                confidence_buckets[bucket_key].append(float(confidence))

            # Communication score
            communication = session.get("communication_score")
            if communication is not None:
                if bucket_key not in communication_buckets:
                    communication_buckets[bucket_key] = []
                communication_buckets[bucket_key].append(float(communication))

        # Build ScoreTrend lists for each category
        def build_trend_series(
            buckets: dict[str, list[float]],
        ) -> list[ScoreTrend]:
            series = []
            for key in sorted(buckets.keys()):
                scores = buckets[key]
                avg = round(sum(scores) / len(scores), 1)
                series.append(
                    ScoreTrend(
                        date=key,
                        average_score=avg,
                        session_count=session_counts.get(key, 0),
                    )
                )
            return series

        trends = AnalyticsTrends(
            overall_scores=build_trend_series(overall_buckets),
            confidence_scores=build_trend_series(confidence_buckets),
            communication_scores=build_trend_series(communication_buckets),
        )

        return {
            "has_sessions": has_sessions,
            "has_enough_data": has_enough_data,
            "trends": trends,
        }


def get_analytics_service() -> AnalyticsService:
    """Factory function for AnalyticsService dependency injection."""
    return AnalyticsService()
