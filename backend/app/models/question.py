"""Question model for interview question generation."""

from typing import Optional

from pydantic import BaseModel, Field


class Question(BaseModel):
    """Represents a single interview question."""

    text: str = Field(..., description="The question text")
    topic: Optional[str] = Field(default=None, description="Topic category")
    difficulty: Optional[str] = Field(default=None, description="Difficulty level")
    interview_type: Optional[str] = Field(
        default=None, description="Type of interview this question belongs to"
    )
    follow_up: Optional[str] = Field(
        default=None, description="Suggested follow-up question"
    )


class QuestionGenerationResult(BaseModel):
    """Result of question generation including fallback metadata."""

    questions: list[Question] = Field(
        default_factory=list, description="Generated questions"
    )
    fallback_used: bool = Field(
        default=False,
        description="Whether fallback question bank was used instead of AI",
    )
    source: str = Field(
        default="gemini",
        description="Source of questions: 'gemini', 'cache', or 'fallback'",
    )
