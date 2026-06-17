import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { InterviewSetup } from "../components/InterviewSetup";
import {
  createInterviewSession,
  createTechnicalSession,
} from "../services/interviewService";
import type { InterviewSetupFormData, TechnicalSetupFormData } from "../schemas/interviewSchemas";

export function InterviewSetupPage() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleStartInterview = async (data: InterviewSetupFormData) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await createInterviewSession({
        interview_type: data.interviewType,
        role: data.role,
        topic: data.topic || undefined,
        difficulty: data.difficulty || undefined,
        num_questions: data.numQuestions,
      });
      navigate(`/interview/session/${result.session.id}`, {
        state: {
          session: result.session,
          questions: result.questions,
          questionSource: result.question_source,
          fallbackUsed: result.fallback_used,
          isTechnical: false,
        },
      });
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Failed to create session";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartTechnical = async (data: TechnicalSetupFormData) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await createTechnicalSession({
        topic: data.topic,
        difficulty: data.difficulty,
        role: data.role,
        num_questions: data.numQuestions,
      });
      navigate(`/interview/session/${result.session.id}`, {
        state: {
          session: result.session,
          questions: result.questions,
          questionSource: result.question_source,
          fallbackUsed: result.fallback_used,
          isTechnical: true,
        },
      });
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Failed to create session";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="py-6">
      <InterviewSetup
        onStartInterview={handleStartInterview}
        onStartTechnical={handleStartTechnical}
        isLoading={isLoading}
        error={error}
      />
    </div>
  );
}
