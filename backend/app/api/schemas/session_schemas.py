"""Pydantic schemas for technical interview session API endpoints.

Defines request and response models for technical session creation,
answer submission, evaluation retrieval, and follow-up generation.

Requirements: 5.1, 5.2, 5.3, 5.4
"""

from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.session import Difficulty


class TechnicalTopic(str, Enum):
    """Supported technical interview topics."""

    data_structures = "Data Structures"
    algorithms = "Algorithms"
    operating_systems = "OS"
    dbms = "DBMS"
    computer_networks = "CN"
    oop = "OOP"
    java = "Java"
    python = "Python"
    javascript = "JavaScript"
    react = "React"
    nodejs = "Node.js"
    cloud_computing = "Cloud Computing"


# --- Request Schemas ---


class CreateTechnicalSessionRequest(BaseModel):
    """Request body for creating a new technical interview session."""

    topic: TechnicalTopic = Field(
        ..., description="Technical topic for the interview"
    )
    difficulty: Difficulty = Field(
        ..., description="Difficulty level (beginner, intermediate, advanced)"
    )
    role: str = Field(
        ..., min_length=1, max_length=200, description="Target job role"
    )
    num_questions: int = Field(
        default=5, ge=1, le=20, description="Number of questions to generate"
    )


class FollowUpRequest(BaseModel):
    """Request body for generating a follow-up question on a weak area."""

    question_index: int = Field(
        ..., ge=0, description="Zero-based index of the question with weak answer"
    )
    weak_area: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Description of the weak area to probe further",
    )


# --- Response Schemas ---


class TechnicalQuestionResponse(BaseModel):
    """Question data in technical session API responses."""

    text: str
    topic: Optional[str] = None
    difficulty: Optional[str] = None
    interview_type: Optional[str] = None
    follow_up: Optional[str] = None


class TechnicalSessionResponse(BaseModel):
    """Session data in technical session API responses."""

    id: UUID
    user_id: UUID
    session_type: str
    interview_type: Optional[str] = None
    role: Optional[str] = None
    topic: Optional[str] = None
    difficulty: Optional[str] = None
    status: str
    created_at: str
    completed_at: Optional[str] = None


class CreateTechnicalSessionResponse(BaseModel):
    """Response for technical session creation endpoint."""

    session: TechnicalSessionResponse
    questions: list[TechnicalQuestionResponse]
    question_source: str = Field(
        description="Source of questions: 'gemini', 'cache', or 'fallback'"
    )
    fallback_used: bool = Field(
        description="Whether fallback question bank was used"
    )


class TechnicalEvaluationScore(BaseModel):
    """Score breakdown for a single technical answer evaluation."""

    technical_accuracy: int = Field(
        ..., ge=0, le=100, description="Technical accuracy score (0-100)"
    )
    completeness: int = Field(
        ..., ge=0, le=100, description="Completeness score (0-100)"
    )
    communication: int = Field(
        ..., ge=0, le=100, description="Communication clarity score (0-100)"
    )


class AnswerEvaluation(BaseModel):
    """Evaluation for a single answer in the session."""

    question_index: int
    question_text: str
    transcript: Optional[str] = None
    scores: TechnicalEvaluationScore
    feedback: Optional[str] = None
    weak_areas: list[str] = Field(default_factory=list)


class TechnicalEvaluationResponse(BaseModel):
    """Response for technical evaluation endpoint with full score breakdown."""

    session_id: UUID
    topic: str
    difficulty: str
    total_questions: int
    answered_questions: int
    evaluations: list[AnswerEvaluation]
    average_scores: TechnicalEvaluationScore
    needs_follow_up: bool = Field(
        description="Whether any answer has weak areas needing follow-up"
    )


class SubmitTechnicalAnswerResponse(BaseModel):
    """Response for technical answer submission endpoint."""

    answer_id: UUID
    session_id: UUID
    question_index: int
    transcript: str
    scores: TechnicalEvaluationScore
    feedback: str
    weak_areas: list[str] = Field(default_factory=list)


class FollowUpResponse(BaseModel):
    """Response for follow-up question generation endpoint."""

    question: TechnicalQuestionResponse
    reason: str = Field(
        description="Explanation of why this follow-up was generated"
    )
    original_question_index: int
    weak_area: str
