import { useLocation } from "react-router-dom";
import { LoginForm } from "../components/LoginForm";

export function LoginPage() {
  const location = useLocation();
  const stateMessage = (location.state as { message?: string } | null)?.message;

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-12">
      <div className="w-full max-w-md space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-2xl font-bold tracking-tight text-foreground">
            Welcome Back
          </h1>
          <p className="text-sm text-muted-foreground">
            Sign in to your account to continue practicing
          </p>
        </div>

        {stateMessage && (
          <div className="rounded-md bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 p-3 text-sm text-green-700 dark:text-green-300">
            {stateMessage}
          </div>
        )}

        <LoginForm />
      </div>
    </div>
  );
}
