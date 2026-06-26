import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/shared/lib/supabase";
import { LoadingSpinner } from "@/shared/components/LoadingSpinner";

/**
 * Handles Supabase auth redirects (email verification, magic links, password recovery).
 *
 * When Supabase redirects back after email verification or password recovery,
 * it appends tokens to the URL. The Supabase client automatically detects and
 * exchanges them. This page waits for that exchange to complete, then navigates
 * the user to the appropriate destination:
 * - PASSWORD_RECOVERY → /reset-password
 * - All other events → /dashboard
 */
export function AuthCallbackPage() {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let handled = false;

    // Listen for auth state changes to detect the event type
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (event, session) => {
        if (handled) return;

        if (event === "PASSWORD_RECOVERY" && session) {
          handled = true;
          subscription.unsubscribe();
          navigate("/reset-password", { replace: true });
          return;
        }

        if (session && (event === "SIGNED_IN" || event === "TOKEN_REFRESHED")) {
          handled = true;
          subscription.unsubscribe();
          navigate("/dashboard", { replace: true });
        }
      }
    );

    // Fallback: if the session is already established (tokens were processed
    // before the listener attached), check and redirect
    async function checkExistingSession() {
      // Small delay to let onAuthStateChange fire first
      await new Promise((resolve) => setTimeout(resolve, 500));
      if (handled) return;

      try {
        const { data, error: sessionError } = await supabase.auth.getSession();

        if (sessionError) {
          console.error("[Auth Callback] Session error:", sessionError.message);
          setError("Verification failed. Please try logging in.");
          setTimeout(() => navigate("/login", { replace: true }), 3000);
          return;
        }

        if (data.session && !handled) {
          // Check if URL hash indicates recovery
          const hash = window.location.hash;
          if (hash.includes("type=recovery")) {
            handled = true;
            subscription.unsubscribe();
            navigate("/reset-password", { replace: true });
          } else {
            handled = true;
            subscription.unsubscribe();
            navigate("/dashboard", { replace: true });
          }
        }
      } catch (err) {
        console.error("[Auth Callback] Unexpected error:", err);
        setError("Something went wrong. Redirecting to login...");
        setTimeout(() => navigate("/login", { replace: true }), 3000);
      }
    }

    checkExistingSession();

    // Timeout: if nothing happens after 8s, redirect to login
    const timeout = setTimeout(() => {
      if (!handled) {
        handled = true;
        subscription.unsubscribe();
        navigate("/login", { replace: true });
      }
    }, 8000);

    return () => {
      clearTimeout(timeout);
      subscription.unsubscribe();
    };
  }, [navigate]);

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center px-4">
        <div className="text-center space-y-4">
          <p className="text-destructive">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center">
      <LoadingSpinner size="lg" label="Verifying your account..." />
    </div>
  );
}
