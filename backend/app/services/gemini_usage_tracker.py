"""Gemini API usage tracker for monitoring and rate limit awareness.

Tracks request counts, token usage estimates, cache hit/miss ratios,
and feedback source (AI vs algorithmic fallback). Designed to help
stay within free-tier rate limits.

Target: Maximum 2 Gemini requests per interview session.
With caching: Maximum 1 Gemini request per interview session.
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class RequestType(str, Enum):
    """Type of Gemini API request."""

    QUESTION_GENERATION = "question_generation"
    FEEDBACK_GENERATION = "feedback_generation"
    RESUME_QUESTIONS = "resume_questions"


class FeedbackSource(str, Enum):
    """Source of feedback generation."""

    GEMINI_AI = "gemini_ai"
    ALGORITHMIC_FALLBACK = "algorithmic_fallback"


@dataclass
class RequestRecord:
    """Record of a single Gemini API request."""

    request_type: RequestType
    timestamp: float
    success: bool
    estimated_input_tokens: int = 0
    estimated_output_tokens: int = 0
    session_id: Optional[str] = None
    error: Optional[str] = None


@dataclass
class SessionUsageStats:
    """Usage statistics for a single interview session."""

    session_id: str
    gemini_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    feedback_source: Optional[FeedbackSource] = None
    questions_source: str = "unknown"  # "cache", "gemini", "fallback"
    total_input_tokens: int = 0
    total_output_tokens: int = 0


class GeminiUsageTracker:
    """Tracks and logs Gemini API usage across the application.

    Singleton-like tracker that maintains request history and
    per-session statistics to monitor free-tier usage.

    Free-tier limits (gemini-2.5-flash):
    - Requests per minute: varies
    - Requests per day: limited
    - Tokens per minute: limited

    Goal: ≤2 requests per session (1 questions + 1 feedback)
    With caching: ≤1 request per session (feedback only)
    """

    _instance: Optional["GeminiUsageTracker"] = None

    def __new__(cls) -> "GeminiUsageTracker":
        """Singleton pattern for global usage tracking."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize tracker state (only once due to singleton)."""
        if self._initialized:
            return
        self._initialized = True
        self._requests: list[RequestRecord] = []
        self._session_stats: dict[str, SessionUsageStats] = {}
        self._daily_request_count = 0
        self._daily_reset_time = time.time()

    def _check_daily_reset(self) -> None:
        """Reset daily counter if a new day has started."""
        now = time.time()
        if now - self._daily_reset_time >= 86400:  # 24 hours
            self._daily_request_count = 0
            self._daily_reset_time = now

    def record_request(
        self,
        request_type: RequestType,
        success: bool,
        session_id: Optional[str] = None,
        estimated_input_tokens: int = 0,
        estimated_output_tokens: int = 0,
        error: Optional[str] = None,
    ) -> None:
        """Record a Gemini API request.

        Args:
            request_type: Type of request made.
            success: Whether the request succeeded.
            session_id: Optional session ID for per-session tracking.
            estimated_input_tokens: Estimated input token count.
            estimated_output_tokens: Estimated output token count.
            error: Error message if request failed.
        """
        self._check_daily_reset()

        record = RequestRecord(
            request_type=request_type,
            timestamp=time.time(),
            success=success,
            estimated_input_tokens=estimated_input_tokens,
            estimated_output_tokens=estimated_output_tokens,
            session_id=session_id,
            error=error,
        )
        self._requests.append(record)

        if success:
            self._daily_request_count += 1

        # Update session stats
        if session_id:
            stats = self._get_or_create_session_stats(session_id)
            if success:
                stats.gemini_requests += 1
                stats.total_input_tokens += estimated_input_tokens
                stats.total_output_tokens += estimated_output_tokens

        # Log the request
        logger.info(
            "GEMINI_USAGE | type=%s | success=%s | session=%s | "
            "input_tokens≈%d | output_tokens≈%d | daily_total=%d%s",
            request_type.value,
            success,
            session_id or "N/A",
            estimated_input_tokens,
            estimated_output_tokens,
            self._daily_request_count,
            f" | error={error}" if error else "",
        )

    def record_cache_event(
        self, hit: bool, session_id: Optional[str] = None
    ) -> None:
        """Record a cache hit or miss.

        Args:
            hit: True for cache hit, False for cache miss.
            session_id: Optional session ID.
        """
        if session_id:
            stats = self._get_or_create_session_stats(session_id)
            if hit:
                stats.cache_hits += 1
            else:
                stats.cache_misses += 1

        logger.info(
            "GEMINI_CACHE | %s | session=%s",
            "HIT" if hit else "MISS",
            session_id or "N/A",
        )

    def record_feedback_source(
        self, source: FeedbackSource, session_id: Optional[str] = None
    ) -> None:
        """Record the source of feedback generation.

        Args:
            source: Whether feedback came from Gemini or algorithmic fallback.
            session_id: Optional session ID.
        """
        if session_id:
            stats = self._get_or_create_session_stats(session_id)
            stats.feedback_source = source

        logger.info(
            "GEMINI_FEEDBACK_SOURCE | source=%s | session=%s",
            source.value,
            session_id or "N/A",
        )

    def record_questions_source(
        self, source: str, session_id: Optional[str] = None
    ) -> None:
        """Record the source of question generation.

        Args:
            source: "cache", "gemini", or "fallback".
            session_id: Optional session ID.
        """
        if session_id:
            stats = self._get_or_create_session_stats(session_id)
            stats.questions_source = source

    def get_session_stats(self, session_id: str) -> Optional[SessionUsageStats]:
        """Get usage statistics for a specific session.

        Args:
            session_id: Session identifier.

        Returns:
            SessionUsageStats or None if session not tracked.
        """
        return self._session_stats.get(session_id)

    def get_daily_request_count(self) -> int:
        """Get the number of Gemini requests made today."""
        self._check_daily_reset()
        return self._daily_request_count

    def get_summary(self) -> dict:
        """Get a summary of overall Gemini usage.

        Returns:
            Dict with usage statistics.
        """
        self._check_daily_reset()
        total_requests = len(self._requests)
        successful = sum(1 for r in self._requests if r.success)
        failed = total_requests - successful

        return {
            "total_requests_lifetime": total_requests,
            "successful_requests": successful,
            "failed_requests": failed,
            "daily_request_count": self._daily_request_count,
            "active_sessions_tracked": len(self._session_stats),
            "total_input_tokens": sum(r.estimated_input_tokens for r in self._requests),
            "total_output_tokens": sum(r.estimated_output_tokens for r in self._requests),
        }

    def _get_or_create_session_stats(self, session_id: str) -> SessionUsageStats:
        """Get or create session stats entry."""
        if session_id not in self._session_stats:
            self._session_stats[session_id] = SessionUsageStats(
                session_id=session_id
            )
        return self._session_stats[session_id]


# Global tracker instance
usage_tracker = GeminiUsageTracker()
