import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { useSessionDetail } from "../hooks/useSessionHistory";
import { SessionDetail } from "../components/SessionDetail";
import { Button } from "@/shared/components/ui/button";
import { ErrorMessage } from "@/shared/components/ErrorMessage";
import { Skeleton } from "@/shared/components/ui/skeleton";

export function SessionDetailPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const { data, isLoading, isError, error, refetch } = useSessionDetail(sessionId || "");

  if (!sessionId) {
    return (
      <ErrorMessage
        message="No session ID provided."
        retry={() => navigate("/history")}
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate("/history")}
          aria-label="Back to history"
        >
          <ArrowLeft className="h-4 w-4" />
          Back
        </Button>
        <h1 className="text-2xl font-bold">Session Details</h1>
      </div>

      {isLoading && (
        <div className="space-y-4">
          <div className="rounded-lg border bg-card p-6 shadow-sm space-y-3">
            <Skeleton className="h-6 w-48" />
            <Skeleton className="h-4 w-32" />
            <div className="grid gap-4 sm:grid-cols-3 mt-4">
              <Skeleton className="h-20 rounded-lg" />
              <Skeleton className="h-20 rounded-lg" />
              <Skeleton className="h-20 rounded-lg" />
            </div>
          </div>
          <div className="rounded-lg border bg-card p-6 shadow-sm space-y-3">
            <Skeleton className="h-5 w-36" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
          </div>
        </div>
      )}

      {isError && (
        <ErrorMessage
          message={
            error instanceof Error
              ? error.message
              : "Failed to load session details."
          }
          retry={() => void refetch()}
        />
      )}

      {data && <SessionDetail session={data} />}
    </div>
  );
}
