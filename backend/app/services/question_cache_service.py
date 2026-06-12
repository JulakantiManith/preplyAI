"""Question cache service for reducing Gemini API calls.

Implements an in-memory cache with configurable TTL for generated
interview questions. Cache key format: {interview_type}:{role}:{topic}:{difficulty}
(normalized to lowercase).

Resume-based questions are never cached (they are personalized per user).

Requirements: 4.1, 5.1 (question generation with caching)
"""

import logging
import time
from typing import Optional

from app.models.question import Question

logger = logging.getLogger(__name__)

# Default cache TTL: 24 hours in seconds
DEFAULT_TTL_SECONDS = 24 * 60 * 60


class CacheEntry:
    """A single cache entry with expiration tracking."""

    def __init__(self, questions: list[Question], ttl_seconds: int) -> None:
        """Initialize cache entry with questions and TTL.

        Args:
            questions: Cached question list.
            ttl_seconds: Time-to-live in seconds.
        """
        self.questions = questions
        self.created_at = time.time()
        self.ttl_seconds = ttl_seconds

    @property
    def is_expired(self) -> bool:
        """Check if this cache entry has expired."""
        return (time.time() - self.created_at) >= self.ttl_seconds


class QuestionCacheService:
    """In-memory cache for generated interview questions.

    Provides cache-aside pattern: check cache first, generate on miss,
    store result for future requests.

    Cache key format: {interview_type}:{role}:{topic}:{difficulty}
    All key components are normalized to lowercase.
    """

    def __init__(self, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> None:
        """Initialize the cache service.

        Args:
            ttl_seconds: Time-to-live for cache entries. Defaults to 24 hours.
        """
        self._cache: dict[str, CacheEntry] = {}
        self._ttl_seconds = ttl_seconds

    @staticmethod
    def _build_cache_key(
        interview_type: str,
        role: str,
        topic: Optional[str] = None,
        difficulty: Optional[str] = None,
    ) -> str:
        """Build a normalized cache key from parameters.

        Args:
            interview_type: Type of interview.
            role: Target job role.
            topic: Optional topic.
            difficulty: Optional difficulty level.

        Returns:
            Normalized cache key string.
        """
        parts = [
            interview_type.lower().strip(),
            role.lower().strip(),
            (topic or "general").lower().strip(),
            (difficulty or "intermediate").lower().strip(),
        ]
        return ":".join(parts)

    async def get_cached_questions(
        self,
        interview_type: str,
        role: str,
        topic: Optional[str] = None,
        difficulty: Optional[str] = None,
    ) -> Optional[list[Question]]:
        """Return cached questions if available and not expired, None on miss.

        Args:
            interview_type: Type of interview.
            role: Target job role.
            topic: Optional topic.
            difficulty: Optional difficulty level.

        Returns:
            List of cached questions or None if cache miss/expired.
        """
        key = self._build_cache_key(interview_type, role, topic, difficulty)
        entry = self._cache.get(key)

        if entry is None:
            logger.debug("Cache miss for key: %s", key)
            return None

        if entry.is_expired:
            logger.debug("Cache expired for key: %s", key)
            del self._cache[key]
            return None

        logger.debug("Cache hit for key: %s", key)
        return entry.questions

    async def cache_questions(
        self,
        interview_type: str,
        role: str,
        questions: list[Question],
        topic: Optional[str] = None,
        difficulty: Optional[str] = None,
    ) -> None:
        """Store generated questions in cache.

        Args:
            interview_type: Type of interview.
            role: Target job role.
            questions: Questions to cache.
            topic: Optional topic.
            difficulty: Optional difficulty level.
        """
        key = self._build_cache_key(interview_type, role, topic, difficulty)
        self._cache[key] = CacheEntry(questions, self._ttl_seconds)
        logger.debug("Cached %d questions for key: %s", len(questions), key)

    async def invalidate_cache(self, pattern: Optional[str] = None) -> None:
        """Invalidate cache entries matching pattern, or all if None.

        Args:
            pattern: Optional pattern to match against cache keys.
                     If None, clears entire cache.
                     Supports prefix matching (e.g., "technical:" matches
                     all technical interview entries).
        """
        if pattern is None:
            count = len(self._cache)
            self._cache.clear()
            logger.info("Invalidated entire question cache (%d entries)", count)
            return

        pattern_lower = pattern.lower()
        keys_to_remove = [
            key for key in self._cache if pattern_lower in key
        ]

        for key in keys_to_remove:
            del self._cache[key]

        logger.info(
            "Invalidated %d cache entries matching pattern: %s",
            len(keys_to_remove),
            pattern,
        )

    @property
    def size(self) -> int:
        """Return the number of entries currently in the cache."""
        return len(self._cache)

    async def cleanup_expired(self) -> int:
        """Remove all expired entries from the cache.

        Returns:
            Number of entries removed.
        """
        expired_keys = [
            key for key, entry in self._cache.items() if entry.is_expired
        ]

        for key in expired_keys:
            del self._cache[key]

        if expired_keys:
            logger.info("Cleaned up %d expired cache entries", len(expired_keys))

        return len(expired_keys)
