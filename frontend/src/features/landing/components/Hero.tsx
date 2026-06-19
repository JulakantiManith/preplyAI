import { Link } from "react-router-dom";
import { Button } from "@/shared/components/ui/button";
import { ThemeToggle } from "@/shared/components/ThemeToggle";
import { useAuth } from "@/features/auth/hooks/useAuth";
import { Mic, Sparkles, LayoutDashboard } from "lucide-react";

export function Hero() {
  const { isAuthenticated } = useAuth();
  const appName = import.meta.env.VITE_APP_NAME || "AI Interview & Presentation Coach";

  return (
    <section className="relative overflow-hidden bg-background">
      {/* Landing Navigation */}
      <nav
        className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8"
        aria-label="Landing page navigation"
      >
        <div className="flex items-center gap-2">
          <Mic className="h-6 w-6 text-primary" />
          <span className="text-lg font-bold text-foreground">
            {appName}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <ThemeToggle />
          {isAuthenticated ? (
            <Button size="sm" asChild>
              <Link to="/dashboard">
                <LayoutDashboard className="mr-2 h-4 w-4" />
                Dashboard
              </Link>
            </Button>
          ) : (
            <>
              <Button variant="ghost" size="sm" asChild>
                <Link to="/login">Sign In</Link>
              </Button>
              <Button size="sm" asChild>
                <Link to="/register">Register</Link>
              </Button>
            </>
          )}
        </div>
      </nav>

      {/* Hero Content */}
      <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 sm:py-28 lg:px-8 lg:py-36">
        <div className="flex flex-col items-center text-center">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border bg-secondary px-4 py-1.5 text-sm text-secondary-foreground">
            <Sparkles className="h-4 w-4" />
            <span>AI-Powered Interview &amp; Presentation Coach</span>
          </div>
          <h1 className="max-w-4xl text-4xl font-bold tracking-tight text-foreground sm:text-5xl lg:text-6xl">
            Practice Smarter,{" "}
            <span className="text-primary">Perform Better</span>
          </h1>
          <p className="mt-6 max-w-2xl text-lg text-muted-foreground sm:text-xl">
            Get real-time AI feedback on your interview answers and
            presentations. Build confidence, improve clarity, and land your
            dream role.
          </p>
          <div className="mt-10 flex flex-col gap-4 sm:flex-row">
            {isAuthenticated ? (
              <Button size="lg" asChild>
                <Link to="/dashboard">Go to Dashboard</Link>
              </Button>
            ) : (
              <>
                <Button size="lg" asChild>
                  <Link to="/register">Get Started Free</Link>
                </Button>
                <Button variant="outline" size="lg" asChild>
                  <Link to="/login">Sign In</Link>
                </Button>
              </>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
