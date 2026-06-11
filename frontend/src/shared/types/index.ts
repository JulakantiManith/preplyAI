// Session and Interview Types

export type SessionType = "interview" | "presentation";

export type InterviewType =
  | "hr"
  | "technical"
  | "behavioral"
  | "custom"
  | "resume_based";

export type Difficulty = "beginner" | "intermediate" | "advanced";

export type SessionStatus = "in_progress" | "completed" | "failed";

// Speech and Analysis

export interface SpeechMetrics {
  wpm: number;
  totalWords: number;
  fillerWordCount: number;
  fillerWords: Record<string, number>;
  speakingDuration: number;
  averagePauseDuration: number;
  communicationScore: number;
  wpmInRange: boolean;
}

export interface ConfidenceResult {
  score: number;
  hesitationCount: number;
  pauseFrequency: number;
  speechFlowScore: number;
  responseCompleteness: number;
}

export interface AIEvaluation {
  score: number;
  feedback: string;
  technicalAccuracy?: number;
  completeness?: number;
  communicationClarity?: number;
}

// Answer and Session

export interface AnswerAnalysis {
  transcript: string;
  speechMetrics: SpeechMetrics;
  confidenceScore: number;
  aiEvaluation: AIEvaluation;
}

export interface SessionReport {
  overallScore: number;
  confidenceScore: number;
  communicationScore: number;
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
  answers: AnswerAnalysis[];
}

export interface InterviewConfig {
  type: InterviewType;
  role: string;
  topic?: string;
  difficulty?: Difficulty;
  questionCount?: number;
}

export interface InterviewSession {
  id: string;
  userId: string;
  sessionType: SessionType;
  interviewType: InterviewType;
  role: string;
  topic?: string;
  difficulty?: Difficulty;
  overallScore?: number;
  confidenceScore?: number;
  communicationScore?: number;
  durationSeconds?: number;
  status: SessionStatus;
  createdAt: string;
  completedAt?: string;
}

// User and Profile

export interface UserProfile {
  id: string;
  userId: string;
  targetRole?: string;
  experienceLevel?: string;
  skills: string[];
  themePreference?: string;
  updatedAt: string;
}

export interface User {
  id: string;
  email: string;
  fullName: string;
  createdAt: string;
  updatedAt: string;
}

// Presentation

export interface PresentationScores {
  speakingSpeed: number;
  clarity: number;
  structure: number;
  communication: number;
  engagement: number;
}

// Session Feedback

export interface SessionFeedback {
  id: string;
  sessionId: string;
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
  technicalEvaluation?: Record<string, unknown>;
  presentationScores?: PresentationScores;
  createdAt: string;
}

// API Response types

export interface ApiError {
  message: string;
  statusCode: number;
  details?: Record<string, string[]>;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}
