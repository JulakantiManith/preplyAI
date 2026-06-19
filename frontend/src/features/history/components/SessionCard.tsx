import { Briefcase, Presentation, Clock } from "lucide-react";
import { cn } from "@/shared/lib/utils";
import type { SessionListItem } from "../services/historyService";

interface SessionCardProps {
  session: SessionListItem;
  onClick: (sessionId: string) => void;
}

function formatDate(isoString: string): string {
  const date = new Date(isoString);
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function formatDuration(seconds: number | null): string {
  if (seconds === null) return "—";
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  if (mins === 0) return `${secs}s`;
  return `${mins}m ${secs}s`;
}

function formatSessionType(type: string): string {
  return type.charAt(0).toUpperCase() + type.slice(1);
}

function SessionIcon({ type }: { type: string }) {
  if (type === "presentation") {
    return <Presentation className="h-5 w-5 text-blue-500" />;
  }
  return <Briefcase className="h-5 w-5 text-purple-500" />;
}

function ScoreBadge({ score }: { score: number | null }) {
  if (score === null) return <span className="text-sm text-muted-foreground">—</span>;

  const colorClass =
    score >= 80
      ? "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400"
      : score >= 60
        ? "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400"
        : "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400";

  return (
    <span
      className={cn("inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium", colorClass)}
    >
      {score}%
    </span>
  );
}

export function SessionCard({ session, onClick }: SessionCardProps) {
  return (
    <button
      onClick={() => onClick(session.id)}
      className="w-full rounded-lg border bg-card p-4 text-left shadow-sm transition-colors hover:bg-accent/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
      aria-label={`View ${formatSessionType(session.sessionType)} session from ${formatDate(session.createdAt)}`}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <SessionIcon type={session.sessionType} />
          <div>
            <p className="text-sm font-medium">
              {formatSessionType(session.sessionType)}
            </p>
            <p className="text-xs text-muted-foreground">
              {formatDate(session.createdAt)}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1 text-xs text-muted-foreground">
            <Clock className="h-3.5 w-3.5" />
            <span>{formatDuration(session.durationSeconds)}</span>
          </div>
          <ScoreBadge score={session.overallScore} />
        </div>
      </div>
    </button>
  );
}
