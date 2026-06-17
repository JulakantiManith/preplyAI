import { Trophy, RotateCcw } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { cn } from "@/shared/lib/utils";
import type { CompleteSessionResponse, TechnicalEvaluationResponse } from "../services/interviewService";

interface SessionReportProps {
  sessionReport: CompleteSessionResponse | null;
  technicalEvaluation: TechnicalEvaluationResponse | null;
  isTechnical: boolean;
  onReset: () => void;
  className?: string;
}

function ScoreCircle({ score, label }: { score: number | null | undefined; label: string }) {
  const displayScore = score ?? 0;
  const percentage = Math.min(displayScore, 100);
  const color =
    percentage >= 70 ? "text-green-500" : percentage >= 40 ? "text-yellow-500" : "text-red-500";

  return (
    <div className="flex flex-col items-center gap-1">
      <div className={cn("text-3xl font-bold", color)}>
        {score != null ? score : "—"}
      </div>
      <span className="text-xs text-muted-foreground">{label}</span>
    </div>
  );
}

export function SessionReport({
  sessionReport,
  technicalEvaluation,
  isTechnical,
  onReset,
  className,
}: SessionReportProps) {
  if (!sessionReport && !technicalEvaluation) {
    return null;
  }

  return (
    <div className={cn("space-y-6", className)}>
      {/* Header */}
      <div className="flex items-center gap-3">
        <Trophy className="h-6 w-6 text-yellow-500" />
        <h2 className="text-2xl font-bold">Session Complete</h2>
      </div>

      {/* Interview Report */}
      {!isTechnical && sessionReport && (
        <div className="space-y-6">
          {/* Scores */}
          <div className="rounded-lg border border-input p-6">
            <h3 className="mb-4 text-sm font-medium text-muted-foreground uppercase tracking-wide">
              Your Scores
            </h3>
            <div className="grid grid-cols-3 gap-4">
              <ScoreCircle score={sessionReport.scores.overall_score} label="Overall" />
              <ScoreCircle score={sessionReport.scores.confidence_score} label="Confidence" />
              <ScoreCircle score={sessionReport.scores.communication_score} label="Communication" />
            </div>
          </div>

          {/* Feedback - Strengths */}
          {sessionReport.feedback && sessionReport.feedback.strengths.length > 0 && (
            <div className="rounded-lg border border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-900/20 p-6 space-y-3">
              <h3 className="text-sm font-medium text-green-800 dark:text-green-300 uppercase tracking-wide">
                Strengths
              </h3>
              <ul className="space-y-2">
                {sessionReport.feedback.strengths.map((s, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-green-700 dark:text-green-400">
                    <span className="mt-1 shrink-0">✓</span>
                    <span>{s}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Feedback - Weaknesses */}
          {sessionReport.feedback && sessionReport.feedback.weaknesses.length > 0 && (
            <div className="rounded-lg border border-yellow-200 dark:border-yellow-800 bg-yellow-50 dark:bg-yellow-900/20 p-6 space-y-3">
              <h3 className="text-sm font-medium text-yellow-800 dark:text-yellow-300 uppercase tracking-wide">
                Areas to Improve
              </h3>
              <ul className="space-y-2">
                {sessionReport.feedback.weaknesses.map((w, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-yellow-700 dark:text-yellow-400">
                    <span className="mt-1 shrink-0">•</span>
                    <span>{w}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Feedback - Recommendations */}
          {sessionReport.feedback && sessionReport.feedback.recommendations.length > 0 && (
            <div className="rounded-lg border border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-900/20 p-6 space-y-3">
              <h3 className="text-sm font-medium text-blue-800 dark:text-blue-300 uppercase tracking-wide">
                Recommendations
              </h3>
              <ul className="space-y-2">
                {sessionReport.feedback.recommendations.map((r, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-blue-700 dark:text-blue-400">
                    <span className="mt-1 shrink-0">→</span>
                    <span>{r}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Summary */}
          <div className="rounded-lg border border-input p-6 space-y-2">
            <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
              Summary
            </h3>
            <p className="text-sm text-muted-foreground">
              You answered {sessionReport.total_answers} question
              {sessionReport.total_answers !== 1 ? "s" : ""} in this session.
            </p>
          </div>
        </div>
      )}

      {/* Technical Evaluation */}
      {isTechnical && technicalEvaluation && (
        <div className="space-y-6">
          {/* Average Scores */}
          <div className="rounded-lg border border-input p-6">
            <h3 className="mb-4 text-sm font-medium text-muted-foreground uppercase tracking-wide">
              Average Scores
            </h3>
            <div className="grid grid-cols-3 gap-4">
              <ScoreCircle
                score={technicalEvaluation.average_scores.technical_accuracy}
                label="Technical"
              />
              <ScoreCircle
                score={technicalEvaluation.average_scores.completeness}
                label="Completeness"
              />
              <ScoreCircle
                score={technicalEvaluation.average_scores.communication}
                label="Communication"
              />
            </div>
          </div>

          {/* Session Info */}
          <div className="rounded-lg border border-input p-6 space-y-2">
            <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
              Session Info
            </h3>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <span className="text-muted-foreground">Topic:</span>
              <span className="font-medium">{technicalEvaluation.topic}</span>
              <span className="text-muted-foreground">Difficulty:</span>
              <span className="font-medium capitalize">{technicalEvaluation.difficulty}</span>
              <span className="text-muted-foreground">Questions Answered:</span>
              <span className="font-medium">
                {technicalEvaluation.answered_questions} / {technicalEvaluation.total_questions}
              </span>
            </div>
          </div>

          {/* Per-question evaluations */}
          {technicalEvaluation.evaluations.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
                Question Breakdown
              </h3>
              {technicalEvaluation.evaluations.map((evaluation, index) => (
                <div key={index} className="rounded-md border border-input p-4 space-y-2">
                  <p className="text-sm font-medium">
                    Q{evaluation.question_index + 1}: {evaluation.question_text}
                  </p>
                  <p className="text-xs text-muted-foreground italic">
                    &quot;{evaluation.transcript}&quot;
                  </p>
                  {evaluation.feedback && (
                    <p className="text-sm text-muted-foreground">{evaluation.feedback}</p>
                  )}
                  {evaluation.weak_areas.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {evaluation.weak_areas.map((area, i) => (
                        <span
                          key={i}
                          className="rounded-full bg-yellow-100 px-2 py-0.5 text-xs text-yellow-800"
                        >
                          {area}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Action */}
      <Button onClick={onReset} variant="outline" className="w-full gap-2">
        <RotateCcw className="h-4 w-4" />
        Start New Session
      </Button>
    </div>
  );
}
