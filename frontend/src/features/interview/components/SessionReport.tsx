import {
  Trophy,
  RotateCcw,
  TrendingUp,
  TrendingDown,
  Lightbulb,
  Target,
  Award,
} from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { cn } from "@/shared/lib/utils";
import type {
  CompleteSessionResponse,
  TechnicalEvaluationResponse,
} from "../services/interviewService";

interface SessionReportProps {
  sessionReport: CompleteSessionResponse | null;
  technicalEvaluation: TechnicalEvaluationResponse | null;
  isTechnical: boolean;
  onReset: () => void;
  className?: string;
}

function ScoreGauge({
  score,
  label,
  size = "lg",
}: {
  score: number | null | undefined;
  label: string;
  size?: "sm" | "lg";
}) {
  const displayScore = score ?? 0;
  const percentage = Math.min(displayScore, 100);
  const circumference = 2 * Math.PI * 40;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  const color =
    percentage >= 70
      ? "text-green-500 dark:text-green-400"
      : percentage >= 40
        ? "text-yellow-500 dark:text-yellow-400"
        : "text-red-500 dark:text-red-400";

  const strokeColor =
    percentage >= 70
      ? "stroke-green-500 dark:stroke-green-400"
      : percentage >= 40
        ? "stroke-yellow-500 dark:stroke-yellow-400"
        : "stroke-red-500 dark:stroke-red-400";

  const bgStroke = "stroke-muted";

  if (size === "sm") {
    return (
      <div className="flex flex-col items-center gap-1.5">
        <div className="relative h-16 w-16">
          <svg className="h-16 w-16 -rotate-90" viewBox="0 0 100 100">
            <circle
              cx="50"
              cy="50"
              r="40"
              fill="none"
              strokeWidth="8"
              className={bgStroke}
            />
            <circle
              cx="50"
              cy="50"
              r="40"
              fill="none"
              strokeWidth="8"
              strokeLinecap="round"
              className={cn(strokeColor, "transition-all duration-1000 ease-out")}
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className={cn("text-sm font-bold", color)}>
              {score != null ? score : "—"}
            </span>
          </div>
        </div>
        <span className="text-xs text-muted-foreground text-center">{label}</span>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative h-24 w-24">
        <svg className="h-24 w-24 -rotate-90" viewBox="0 0 100 100">
          <circle
            cx="50"
            cy="50"
            r="40"
            fill="none"
            strokeWidth="7"
            className={bgStroke}
          />
          <circle
            cx="50"
            cy="50"
            r="40"
            fill="none"
            strokeWidth="7"
            strokeLinecap="round"
            className={cn(strokeColor, "transition-all duration-1000 ease-out")}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={cn("text-2xl font-bold", color)}>
            {score != null ? score : "—"}
          </span>
        </div>
      </div>
      <span className="text-xs font-medium text-muted-foreground">{label}</span>
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
    <div className={cn("space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500", className)}>
      {/* Header */}
      <div className="flex flex-col items-center gap-3 text-center py-4">
        <div className="rounded-full bg-yellow-100 dark:bg-yellow-500/20 p-3">
          <Trophy className="h-8 w-8 text-yellow-600 dark:text-yellow-400" />
        </div>
        <div>
          <h2 className="text-2xl font-bold">Session Complete!</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Here&apos;s how you performed
          </p>
        </div>
      </div>

      {/* Interview Report */}
      {!isTechnical && sessionReport && (
        <div className="space-y-5">
          {/* Scores */}
          <div className="rounded-xl border border-input bg-card p-6 shadow-sm">
            <div className="flex items-center gap-2 mb-5">
              <Award className="h-4 w-4 text-primary" />
              <h3 className="text-sm font-semibold text-foreground uppercase tracking-wide">
                Your Scores
              </h3>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <ScoreGauge score={sessionReport.scores.overall_score} label="Overall" />
              <ScoreGauge score={sessionReport.scores.confidence_score} label="Confidence" />
              <ScoreGauge score={sessionReport.scores.communication_score} label="Communication" />
            </div>
          </div>

          {/* Feedback - Strengths */}
          {sessionReport.feedback && sessionReport.feedback.strengths.length > 0 && (
            <div className="rounded-xl border border-green-200 dark:border-green-800 bg-gradient-to-br from-green-50 to-emerald-50/50 dark:from-green-900/20 dark:to-emerald-900/10 p-5 space-y-3 animate-in fade-in slide-in-from-left-2 duration-400">
              <div className="flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-green-600 dark:text-green-400" />
                <h3 className="text-sm font-semibold text-green-800 dark:text-green-300 uppercase tracking-wide">
                  Strengths
                </h3>
              </div>
              <ul className="space-y-2">
                {sessionReport.feedback.strengths.map((s, i) => (
                  <li
                    key={i}
                    className="flex items-start gap-2 text-sm text-green-700 dark:text-green-400"
                  >
                    <span className="mt-0.5 shrink-0 h-5 w-5 rounded-full bg-green-200 dark:bg-green-800 flex items-center justify-center text-xs font-medium text-green-700 dark:text-green-300">
                      ✓
                    </span>
                    <span>{s}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Feedback - Weaknesses */}
          {sessionReport.feedback && sessionReport.feedback.weaknesses.length > 0 && (
            <div className="rounded-xl border border-yellow-200 dark:border-yellow-800 bg-gradient-to-br from-yellow-50 to-amber-50/50 dark:from-yellow-900/20 dark:to-amber-900/10 p-5 space-y-3 animate-in fade-in slide-in-from-left-2 duration-400">
              <div className="flex items-center gap-2">
                <TrendingDown className="h-4 w-4 text-yellow-600 dark:text-yellow-400" />
                <h3 className="text-sm font-semibold text-yellow-800 dark:text-yellow-300 uppercase tracking-wide">
                  Areas to Improve
                </h3>
              </div>
              <ul className="space-y-2">
                {sessionReport.feedback.weaknesses.map((w, i) => (
                  <li
                    key={i}
                    className="flex items-start gap-2 text-sm text-yellow-700 dark:text-yellow-400"
                  >
                    <span className="mt-0.5 shrink-0 h-5 w-5 rounded-full bg-yellow-200 dark:bg-yellow-800 flex items-center justify-center text-xs font-medium text-yellow-700 dark:text-yellow-300">
                      !
                    </span>
                    <span>{w}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Feedback - Recommendations */}
          {sessionReport.feedback && sessionReport.feedback.recommendations.length > 0 && (
            <div className="rounded-xl border border-blue-200 dark:border-blue-800 bg-gradient-to-br from-blue-50 to-indigo-50/50 dark:from-blue-900/20 dark:to-indigo-900/10 p-5 space-y-3 animate-in fade-in slide-in-from-left-2 duration-400">
              <div className="flex items-center gap-2">
                <Lightbulb className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                <h3 className="text-sm font-semibold text-blue-800 dark:text-blue-300 uppercase tracking-wide">
                  Recommendations
                </h3>
              </div>
              <ul className="space-y-2">
                {sessionReport.feedback.recommendations.map((r, i) => (
                  <li
                    key={i}
                    className="flex items-start gap-2 text-sm text-blue-700 dark:text-blue-400"
                  >
                    <span className="mt-0.5 shrink-0 h-5 w-5 rounded-full bg-blue-200 dark:bg-blue-800 flex items-center justify-center text-xs font-medium text-blue-700 dark:text-blue-300">
                      →
                    </span>
                    <span>{r}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Summary */}
          <div className="rounded-xl border border-input bg-card p-5 space-y-2 shadow-sm">
            <div className="flex items-center gap-2">
              <Target className="h-4 w-4 text-muted-foreground" />
              <h3 className="text-sm font-semibold text-foreground uppercase tracking-wide">
                Summary
              </h3>
            </div>
            <p className="text-sm text-muted-foreground">
              You answered {sessionReport.total_answers} question
              {sessionReport.total_answers !== 1 ? "s" : ""} in this session.
            </p>
          </div>
        </div>
      )}

      {/* Technical Evaluation */}
      {isTechnical && technicalEvaluation && (
        <div className="space-y-5">
          {/* Average Scores */}
          <div className="rounded-xl border border-input bg-card p-6 shadow-sm">
            <div className="flex items-center gap-2 mb-5">
              <Award className="h-4 w-4 text-primary" />
              <h3 className="text-sm font-semibold text-foreground uppercase tracking-wide">
                Average Scores
              </h3>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <ScoreGauge
                score={technicalEvaluation.average_scores.technical_accuracy}
                label="Technical"
              />
              <ScoreGauge
                score={technicalEvaluation.average_scores.completeness}
                label="Completeness"
              />
              <ScoreGauge
                score={technicalEvaluation.average_scores.communication}
                label="Communication"
              />
            </div>
          </div>

          {/* Session Info */}
          <div className="rounded-xl border border-input bg-card p-5 space-y-3 shadow-sm">
            <h3 className="text-sm font-semibold text-foreground uppercase tracking-wide">
              Session Info
            </h3>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <span className="text-muted-foreground">Topic:</span>
              <span className="font-medium">{technicalEvaluation.topic}</span>
              <span className="text-muted-foreground">Difficulty:</span>
              <span className="font-medium capitalize">
                {technicalEvaluation.difficulty}
              </span>
              <span className="text-muted-foreground">Questions Answered:</span>
              <span className="font-medium">
                {technicalEvaluation.answered_questions} /{" "}
                {technicalEvaluation.total_questions}
              </span>
            </div>
          </div>

          {/* Per-question evaluations */}
          {technicalEvaluation.evaluations.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-sm font-semibold text-foreground uppercase tracking-wide">
                Question Breakdown
              </h3>
              {technicalEvaluation.evaluations.map((evaluation, index) => (
                <div
                  key={index}
                  className="rounded-xl border border-input bg-card p-5 space-y-3 shadow-sm animate-in fade-in slide-in-from-bottom-2 duration-300"
                  style={{ animationDelay: `${index * 100}ms` }}
                >
                  <p className="text-sm font-semibold">
                    Q{evaluation.question_index + 1}: {evaluation.question_text}
                  </p>
                  <p className="text-xs text-muted-foreground italic border-l-2 border-muted pl-3">
                    &quot;{evaluation.transcript}&quot;
                  </p>
                  {evaluation.feedback && (
                    <p className="text-sm text-muted-foreground">
                      {evaluation.feedback}
                    </p>
                  )}
                  {evaluation.weak_areas.length > 0 && (
                    <div className="flex flex-wrap gap-1.5">
                      {evaluation.weak_areas.map((area, i) => (
                        <span
                          key={i}
                          className="rounded-full bg-yellow-100 dark:bg-yellow-500/20 px-2.5 py-0.5 text-xs font-medium text-yellow-800 dark:text-yellow-300"
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
      <Button
        onClick={onReset}
        variant="outline"
        className="w-full gap-2 h-11 text-base transition-transform duration-200 hover:scale-[1.01]"
      >
        <RotateCcw className="h-4 w-4" />
        Start New Session
      </Button>
    </div>
  );
}
