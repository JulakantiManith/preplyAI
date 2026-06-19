import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { useSessionDetail } from "../hooks/useSessionHistory";
import { SessionDetail } from "../components/SessionDetail";
import { Button } from "@/shared/components/ui/button";
import { LoadingSpinner } from "@/shared/components/LoadingSpinner";
import { ErrorMessage } from "@/shared/components/ErrorMessage";

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
        <div className="flex h-64 items-center justify-center">
          <LoadingSpinner label="Loading session details..." />
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
