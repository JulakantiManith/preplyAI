import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { SessionCard } from "./SessionCard";
import type { SessionListItem } from "../services/historyService";

interface SessionListProps {
  sessions: SessionListItem[];
  page: number;
  totalPages: number;
  totalCount: number;
  onPageChange: (page: number) => void;
  onSessionClick: (sessionId: string) => void;
}

export function SessionList({
  sessions,
  page,
  totalPages,
  totalCount,
  onPageChange,
  onSessionClick,
}: SessionListProps) {
  if (sessions.length === 0) {
    return (
      <div className="flex h-48 items-center justify-center rounded-lg border bg-card">
        <p className="text-sm text-muted-foreground">
          No sessions found. Start practicing to build your history.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="space-y-3">
        {sessions.map((session) => (
          <SessionCard
            key={session.id}
            session={session}
            onClick={onSessionClick}
          />
        ))}
      </div>

      {/* Pagination controls */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between border-t pt-4">
          <p className="text-sm text-muted-foreground">
            Showing page {page} of {totalPages} ({totalCount} sessions)
          </p>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => onPageChange(page - 1)}
              disabled={page <= 1}
              aria-label="Previous page"
            >
              <ChevronLeft className="h-4 w-4" />
              Previous
            </Button>
            <span className="text-sm font-medium">{page}</span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onPageChange(page + 1)}
              disabled={page >= totalPages}
              aria-label="Next page"
            >
              Next
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
