import { AlertCircle } from "lucide-react";
import { cn } from "@/shared/lib/utils";

interface ErrorMessageProps {
  title?: string;
  message: string;
  className?: string;
  retry?: () => void;
}

export function ErrorMessage({
  title = "Something went wrong",
  message,
  className,
  retry,
}: ErrorMessageProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-3 rounded-lg border border-destructive/20 bg-destructive/5 p-6 text-center",
        className
      )}
      role="alert"
    >
      <AlertCircle className="h-8 w-8 text-destructive" />
      <div className="space-y-1">
        <h3 className="font-semibold text-destructive">{title}</h3>
        <p className="text-sm text-muted-foreground">{message}</p>
      </div>
      {retry && (
        <button
          onClick={retry}
          className="mt-2 rounded-md bg-destructive px-4 py-2 text-sm font-medium text-destructive-foreground hover:bg-destructive/90 transition-colors"
        >
          Try Again
        </button>
      )}
    </div>
  );
}
