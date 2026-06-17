import { cn } from "@/shared/lib/utils";

interface QuestionDisplayProps {
  questionText: string;
  questionIndex: number;
  totalQuestions: number;
  className?: string;
}

export function QuestionDisplay({
  questionText,
  questionIndex,
  totalQuestions,
  className,
}: QuestionDisplayProps) {
  return (
    <div className={cn("space-y-4", className)}>
      {/* Progress indicator */}
      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <span>
          Question {questionIndex + 1} of {totalQuestions}
        </span>
        <span className="font-medium">
          {Math.round(((questionIndex + 1) / totalQuestions) * 100)}%
        </span>
      </div>

      {/* Progress bar */}
      <div
        className="h-2 w-full rounded-full bg-muted"
        role="progressbar"
        aria-valuemin={0}
        aria-valuemax={totalQuestions}
        aria-valuenow={questionIndex + 1}
        aria-label={`Question ${questionIndex + 1} of ${totalQuestions}`}
      >
        <div
          className="h-2 rounded-full bg-primary transition-all duration-300"
          style={{ width: `${((questionIndex + 1) / totalQuestions) * 100}%` }}
        />
      </div>

      {/* Question text */}
      <div className="rounded-lg border border-input bg-muted/30 p-6">
        <p className="text-lg font-medium leading-relaxed">{questionText}</p>
      </div>
    </div>
  );
}
