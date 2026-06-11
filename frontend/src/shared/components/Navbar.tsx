import { Menu, LogIn, User } from "lucide-react";
import { Link } from "react-router-dom";
import { cn } from "@/shared/lib/utils";
import { Button } from "@/shared/components/ui/button";

interface NavbarProps {
  onToggleSidebar: () => void;
  className?: string;
}

export function Navbar({ onToggleSidebar, className }: NavbarProps) {
  // Placeholder for auth state — will be connected to auth feature later
  const isAuthenticated = false;

  return (
    <header
      className={cn(
        "sticky top-0 z-40 flex h-16 items-center border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 px-4 md:px-6",
        className
      )}
    >
      {/* Mobile sidebar toggle */}
      <button
        onClick={onToggleSidebar}
        className="mr-4 md:hidden rounded-md p-2 hover:bg-accent transition-colors"
        aria-label="Toggle sidebar navigation"
      >
        <Menu className="h-5 w-5" />
      </button>

      {/* Logo / Brand */}
      <Link to="/" className="flex items-center gap-2 font-semibold text-lg">
        <span className="hidden sm:inline">AI Interview Coach</span>
        <span className="sm:hidden">AIC</span>
      </Link>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Auth placeholder */}
      <nav className="flex items-center gap-2">
        {isAuthenticated ? (
          <Button variant="ghost" size="icon" aria-label="User profile">
            <User className="h-5 w-5" />
          </Button>
        ) : (
          <Button variant="default" size="sm" asChild>
            <Link to="/login">
              <LogIn className="mr-2 h-4 w-4" />
              Sign In
            </Link>
          </Button>
        )}
      </nav>
    </header>
  );
}
