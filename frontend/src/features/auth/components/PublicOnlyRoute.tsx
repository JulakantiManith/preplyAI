import { Navigate, Outlet } from "react-router-dom";
import { LoadingSpinner } from "@/shared/components/LoadingSpinner";
import { useAuth } from "../hooks/useAuth";

export function PublicOnlyRoute() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <LoadingSpinner size="lg" label="Loading..." />
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
}
