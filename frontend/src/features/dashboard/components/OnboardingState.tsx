import { Link } from "react-router-dom";
import { Sparkles } from "lucide-react";
import { Button } from "@/shared/components/ui/button";

export function OnboardingState() {
  return (
    <div className="flex flex-col items-center justify-center rounded-lg border border-dashed bg-card/50 px-6 py-12 text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-full bg-primary/10">
        <Sparkles className="h-7 w-7 text-primary" />
      </div>
      <h2 className="mt-4 text-xl font-semibold text-foreground">Welcome to your Dashboard</h2>
      <p className="mt-2 max-w-md text-sm text-muted-foreground">
        Start your first practice session to see your performance metrics,
        progress charts, and session history here.
      </p>
      <Button asChild className="mt-6" size="sm">
        <Link to="/interview">Start Your First Session</Link>
      </Button>
    </div>
  );
}
