"""Pydantic schemas for analytics endpoints."""

from pydantic import BaseModel, Field

from app.models.analytics import AnalyticsOverview, AnalyticsTrends, ScoreTrend


class RecentSession(BaseModel):
    """A single recent session entry for the dashboard."""

    session_type: str
    created_at: str
    overall_score: int | None = None


class AnalyticsOverviewResponse(BaseModel):
    """Response schema for the analytics overview endpoint.

    Includes aggregate metrics, weekly progress chart data,
    and recent sessions for the dashboard.
    """

    has_sessions: bool = Field(
        description="Whether the user has any completed sessions. "
        "If false, the frontend should show onboarding state."
    )
    overview: AnalyticsOverview = Field(
        description="Aggregate metrics for the dashboard cards."
    )
    weekly_progress: list[ScoreTrend] = Field(
        default_factory=list,
        description="Daily score averages for the current week (Monday-Sunday).",
    )
    recent_sessions: list[RecentSession] = Field(
        default_factory=list,
        description="The 5 most recent completed sessions.",
    )


class ProgressDataPoint(BaseModel):
    """A single data point in the progress chart (session frequency)."""

    period: str = Field(
        description="The bucket label (date YYYY-MM-DD, week YYYY-Wnn, or month YYYY-MM)."
    )
    session_count: int = Field(ge=0, description="Number of sessions in this period.")
    average_score: float | None = Field(
        default=None,
        description="Average overall score in this period, or null if no scored sessions.",
    )


class AnalyticsProgressResponse(BaseModel):
    """Response schema for the analytics progress endpoint.

    Provides session frequency data bucketed by day/week/month
    for bar chart display.
    """

    has_sessions: bool = Field(
        description="Whether the user has any completed sessions."
    )
    has_enough_data: bool = Field(
        description="True when user has >= 3 sessions for full trend analysis. "
        "If false, display encouraging message."
    )
    data_points: list[ProgressDataPoint] = Field(
        default_factory=list,
        description="Progress data bucketed by the selected time range.",
    )


class AnalyticsTrendsResponse(BaseModel):
    """Response schema for the analytics trends endpoint.

    Provides independent score trend series for overall, confidence,
    and communication scores.
    """

    has_sessions: bool = Field(
        description="Whether the user has any completed sessions."
    )
    has_enough_data: bool = Field(
        description="True when user has >= 3 sessions for full trend analysis. "
        "If false, display encouraging message."
    )
    trends: AnalyticsTrends = Field(
        default_factory=AnalyticsTrends,
        description="Independent trend series for each score category.",
    )
