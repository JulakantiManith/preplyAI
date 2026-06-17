import apiClient from "@/shared/lib/axios";

export interface CreateInterviewSessionRequest {
  interview_type: string;
  role: string;
  topic?: string;
  difficulty?: string;
  num_questions: number;
}

export interface CreateTechnicalSessionRequest {
  topic: string;
  difficulty: string;
  role: string;
  num_questions: number;
}

export interface SessionQuestion {
  text: string;
  topic?: string | null;
  difficulty?: string | null;
  interview_type?: string | null;
  follow_up?: string | null;
}

// Helper to get question text and index from the questions array
export function getQuestionText(question: SessionQuestion): string {
  return question.text;
}

export interface CreateSessionResponse {
  session: {
    id: string;
    user_id: string;
    session_type: string;
    interview_type?: string;
    status: string;
    created_at: string;
  };
  questions: SessionQuestion[];
  question_source: string;
  fallback_used: boolean;
}

export interface SubmitAnswerResponse {
  answer: {
    id: string;
    session_id: string;
    question_index: number;
    transcript: string;
    scores?: {
      technical_accuracy?: number;
      completeness?: number;
      communication?: number;
    };
    feedback?: string;
  };
  transcript: string;
}

export interface TechnicalAnswerResponse {
  answer_id: string;
  session_id: string;
  question_index: number;
  transcript: string;
  scores: {
    technical_accuracy: number;
    completeness: number;
    communication: number;
  };
  feedback: string;
  weak_areas: string[];
}

export interface SessionFeedback {
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
  technical_evaluation?: Record<string, unknown> | null;
}

export interface CompleteSessionResponse {
  session: {
    id: string;
    status: string;
    overall_score: number | null;
    confidence_score: number | null;
    communication_score: number | null;
    completed_at: string;
  };
  total_answers: number;
  scores: {
    overall_score: number | null;
    confidence_score: number | null;
    communication_score: number | null;
  };
  feedback: SessionFeedback | null;
}

export interface TechnicalEvaluationResponse {
  session_id: string;
  topic: string;
  difficulty: string;
  total_questions: number;
  answered_questions: number;
  evaluations: Array<{
    question_index: number;
    question_text: string;
    transcript: string;
    scores: {
      technical_accuracy: number;
      completeness: number;
      communication: number;
    };
    feedback: string;
    weak_areas: string[];
  }>;
  average_scores: {
    technical_accuracy: number;
    completeness: number;
    communication: number;
  };
  needs_follow_up: boolean;
}

export async function createInterviewSession(
  data: CreateInterviewSessionRequest
): Promise<CreateSessionResponse> {
  const response = await apiClient.post<CreateSessionResponse>(
    "/sessions/interview",
    data
  );
  return response.data;
}

export async function createTechnicalSession(
  data: CreateTechnicalSessionRequest
): Promise<CreateSessionResponse> {
  const response = await apiClient.post<CreateSessionResponse>(
    "/sessions/technical",
    data
  );
  return response.data;
}

export async function submitInterviewAnswer(
  sessionId: string,
  audioBlob: Blob,
  questionIndex: number,
  questionText: string
): Promise<SubmitAnswerResponse> {
  const formData = new FormData();
  formData.append("audio", audioBlob, "answer.webm");
  formData.append("question_index", questionIndex.toString());
  formData.append("question_text", questionText);

  const response = await apiClient.post<SubmitAnswerResponse>(
    `/sessions/interview/${sessionId}/answers`,
    formData,
    { headers: { "Content-Type": "multipart/form-data" } }
  );
  return response.data;
}

export async function submitTechnicalAnswer(
  sessionId: string,
  audioBlob: Blob,
  questionIndex: number,
  questionText: string
): Promise<TechnicalAnswerResponse> {
  const formData = new FormData();
  formData.append("audio", audioBlob, "answer.webm");
  formData.append("question_index", questionIndex.toString());
  formData.append("question_text", questionText);

  const response = await apiClient.post<TechnicalAnswerResponse>(
    `/sessions/technical/${sessionId}/answers`,
    formData,
    { headers: { "Content-Type": "multipart/form-data" } }
  );
  return response.data;
}

export async function completeInterviewSession(
  sessionId: string
): Promise<CompleteSessionResponse> {
  const response = await apiClient.post<CompleteSessionResponse>(
    `/sessions/interview/${sessionId}/complete`
  );
  return response.data;
}

export async function getTechnicalEvaluation(
  sessionId: string
): Promise<TechnicalEvaluationResponse> {
  const response = await apiClient.get<TechnicalEvaluationResponse>(
    `/sessions/technical/${sessionId}/evaluation`
  );
  return response.data;
}
