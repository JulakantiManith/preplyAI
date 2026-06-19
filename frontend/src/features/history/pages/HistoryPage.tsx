import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useSessionHistory } from "../hooks/useSessionHistory";
import { SessionList } from "../components/SessionList";
import { SessionFilters } from "../components/SessionFilters";
import { LoadingSpinner } from "@/shared/components/LoadingSpinner";
import { ErrorMessage } from "@/shared/components/ErrorMessage";
import type { HistoryFilters } from "../services/historyService";

export function HistoryPage() {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState<HistoryFilters>({});

  const { data, isLoading, isError, error, refetch } = useSessionHistory(page, filters);

  function handleFiltersChange(newFilters: HistoryFilters) {
    setFilters(newFilters);
    setPage(1); // Reset to first page when filters change
  }

  function handleSessionClick(sessionId: string) {
    navigate(`/history/${sessionId}`);
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Session History</h1>

      <SessionFilters filters={filters} onFiltersChange={handleFiltersChange} />

      {isLoading && (
        <div className="flex h-48 items-center justify-center">
          <LoadingSpinner label="Loading sessions..." />
        </div>
      )}

      {isError && (
        <ErrorMessage
          message={
            error instanceof Error
              ? error.message
              : "Failed to load session history."
          }
          retry={() => void refetch()}
        />
      )}

      {data && (
        <SessionList
          sessions={data.sessions}
          page={data.page}
          totalPages={data.totalPages}
          totalCount={data.totalCount}
          onPageChange={setPage}
          onSessionClick={handleSessionClick}
        />
      )}
    </div>
  );
}
