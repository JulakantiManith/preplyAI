import { CheckCircle, MessageSquare } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { cn } from "@/shared/lib/utils";
import type { AnswerResult } from "../hooks/useInterview";
import type { TechnicalAnswerResponse, SubmitAnswerResponse } from "../services/interviewService";

interface AnswerFeedbackProps {
  answerResult: AnswerResult;
  isTechnical: boolean;
  isLastQuestion: boolean;
  onNext: () => void;
  onComplete: () => void;
  className?: string;
}

function isTechnicalResponse(
  response: SubmitAnswerResponse | TechnicalAnswerResponse
): response is TechnicalAnswerResponse {
  return "scores" in response && "weak_areas" in response;
}

function ScoreBar({ label, score, maxScore = 10 }: { label: string; score: number; maxScore?: number }) {
  const percentage = Math.min((score / maxScore) * 100, 100);
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span className="text-muted-foreground">{label}</span>
        <span className="font-medium">{score.toFixed(1)}/{maxScore}</span>
      </div>
      <div className="h-2 w-full rounded-full bg-muted">
        <div
          className={cn(
            "h-2 rounded-full transition-all",
            percentage >= 70 ? "bg-green-500" : percentage >= 40 ? "bg-yellow-500" : "bg-red-500"
          )}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

export function AnswerFeedback({
  answerResult,
  isTechnical,
  isLastQuestion,
  onNext,
  onComplete,
  className,
}: AnswerFeedbackProps) {
  const { response } = answerResult;

  return (
    <div className={cn("space-y-6", className)}>
      <div className="flex items-center gap-2">
        <CheckCircle className="h-5 w-5 text-green-500" />
        <h3 className="text-lg font-semibold">Answer Submitted</h3>
      </div>

      {/* Transcript */}
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <MessageSquare className="h-4 w-4 text-muted-foreground" />
          <h4 className="text-sm font-medium">Your Response (Transcript)</h4>
        </div>
        <div className="rounded-md border border-input bg-muted/30 p-4">
          <p className="text-sm leading-relaxed">
            {isTechnicalResponse(response) ? response.transcript : response.transcript}
          </p>
        </div>
      </div>

      {/* Scores - Technical */}
      {isTechnical && isTechnicalResponse(response) && (
        <div className="space-y-3">
          <h4 className="text-sm font-medium">Scores</h4>
          <div className="rounded-md border border-input p-4 space-y-3">
            <ScoreBar label="Technical Accuracy" score={response.scores.technical_accuracy} />
            <ScoreBar label="Completeness" score={response.scores.completeness} />
            <ScoreBar label="Communication" score={response.scores.communication} />
          </div>
        </div>
      )}

      {/* Feedback */}
      {isTechnical && isTechnicalResponse(response) && response.feedback && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium">Feedback</h4>
          <div className="rounded-md border border-input bg-muted/30 p-4">
            <p className="text-sm leading-relaxed">{response.feedback}</p>
          </div>
        </div>
      )}

      {/* Weak Areas */}
      {isTechnical && isTechnicalResponse(response) && response.weak_areas.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium">Areas to Improve</h4>
          <ul className="list-disc list-inside space-y-1">
            {response.weak_areas.map((area, index) => (
              <li key={index} className="text-sm text-muted-foreground">
                {area}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Non-technical basic feedback */}
      {!isTechnical && !isTechnicalResponse(response) && response.answer?.feedback && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium">Feedback</h4>
          <div className="rounded-md border border-input bg-muted/30 p-4">
            <p className="text-sm leading-relaxed">{response.answer.feedback}</p>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-3">
        {isLastQuestion ? (
          <Button onClick={onComplete} className="w-full">
            Complete Session
          </Button>
        ) : (
          <Button onClick={onNext} className="w-full">
            Next Question
          </Button>
        )}
      </div>
    </div>
  );
}
