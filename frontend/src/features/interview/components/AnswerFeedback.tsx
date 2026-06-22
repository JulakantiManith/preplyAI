import { CheckCircle, MessageSquare, TrendingDown } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { cn } from "@/shared/lib/utils";
import type { AnswerResult } from "../hooks/useInterview";
import type {
  TechnicalAnswerResponse,
  SubmitAnswerResponse,
} from "../services/interviewService";

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

function ScoreBar({
  label,
  score,
  maxScore = 10,
}: {
  label: string;
  score: number;
  maxScore?: number;
}) {
  const percentage = Math.min((score / maxScore) * 100, 100);
  const color =
    percentage >= 70
      ? "bg-green-500 dark:bg-green-400"
      : percentage >= 40
        ? "bg-yellow-500 dark:bg-yellow-400"
        : "bg-red-500 dark:bg-red-400";

  return (
    <div className="space-y-1.5">
      <div className="flex justify-between text-sm">
        <span className="text-muted-foreground">{label}</span>
        <span className="font-semibold tabular-nums">
          {score.toFixed(1)}/{maxScore}
        </span>
      </div>
      <div className="h-2.5 w-full rounded-full bg-muted overflow-hidden">
        <div
          className={cn(
            "h-full rounded-full transition-all duration-700 ease-out",
            color
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
    <div className={cn("space-y-5 animate-in fade-in slide-in-from-bottom-3 duration-400", className)}>
      {/* Success header */}
      <div className="flex items-center gap-3 rounded-xl border border-green-200 dark:border-green-800 bg-gradient-to-r from-green-50 to-emerald-50/50 dark:from-green-900/20 dark:to-emerald-900/10 p-4">
        <div className="rounded-full bg-green-200 dark:bg-green-800 p-1.5">
          <CheckCircle className="h-4 w-4 text-green-600 dark:text-green-400" />
        </div>
        <h3 className="text-base font-semibold text-green-800 dark:text-green-300">
          Answer Submitted
        </h3>
      </div>

      {/* Transcript */}
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <MessageSquare className="h-4 w-4 text-muted-foreground" />
          <h4 className="text-sm font-medium">Your Response</h4>
        </div>
        <div className="rounded-lg border border-input bg-muted/30 p-4 border-l-4 border-l-primary/30">
          <p className="text-sm leading-relaxed">
            {isTechnicalResponse(response)
              ? response.transcript
              : response.transcript}
          </p>
        </div>
      </div>

      {/* Scores - Technical */}
      {isTechnical && isTechnicalResponse(response) && (
        <div className="space-y-3">
          <h4 className="text-sm font-medium">Scores</h4>
          <div className="rounded-xl border border-input bg-card p-4 space-y-3 shadow-sm">
            <ScoreBar
              label="Technical Accuracy"
              score={response.scores.technical_accuracy}
            />
            <ScoreBar
              label="Completeness"
              score={response.scores.completeness}
            />
            <ScoreBar
              label="Communication"
              score={response.scores.communication}
            />
          </div>
        </div>
      )}

      {/* Feedback */}
      {isTechnical && isTechnicalResponse(response) && response.feedback && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium">Feedback</h4>
          <div className="rounded-lg border border-input bg-muted/20 p-4">
            <p className="text-sm leading-relaxed text-muted-foreground">
              {response.feedback}
            </p>
          </div>
        </div>
      )}

      {/* Weak Areas */}
      {isTechnical &&
        isTechnicalResponse(response) &&
        response.weak_areas.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <TrendingDown className="h-4 w-4 text-yellow-600 dark:text-yellow-400" />
              <h4 className="text-sm font-medium">Areas to Improve</h4>
            </div>
            <div className="flex flex-wrap gap-2">
              {response.weak_areas.map((area, index) => (
                <span
                  key={index}
                  className="rounded-full bg-yellow-100 dark:bg-yellow-500/20 border border-yellow-200 dark:border-yellow-700 px-3 py-1 text-xs font-medium text-yellow-800 dark:text-yellow-300"
                >
                  {area}
                </span>
              ))}
            </div>
          </div>
        )}

      {/* Non-technical basic feedback */}
      {!isTechnical &&
        !isTechnicalResponse(response) &&
        response.answer?.feedback && (
          <div className="space-y-2">
            <h4 className="text-sm font-medium">Feedback</h4>
            <div className="rounded-lg border border-input bg-muted/20 p-4">
              <p className="text-sm leading-relaxed text-muted-foreground">
                {response.answer.feedback}
              </p>
            </div>
          </div>
        )}

      {/* Actions */}
      <div className="flex gap-3 pt-2">
        {isLastQuestion ? (
          <Button
            onClick={onComplete}
            className="w-full h-11 text-base font-medium transition-transform duration-200 hover:scale-[1.01]"
          >
            Complete Session
          </Button>
        ) : (
          <Button
            onClick={onNext}
            className="w-full h-11 text-base font-medium transition-transform duration-200 hover:scale-[1.01]"
          >
            Next Question
          </Button>
        )}
      </div>
    </div>
  );
}
