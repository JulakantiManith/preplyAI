import { useState } from "react";
import { Menu, LogIn, LogOut, UserPlus, User } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { cn } from "@/shared/lib/utils";
import { Button } from "@/shared/components/ui/button";
import { ThemeToggle } from "@/shared/components/ThemeToggle";
import { useAuth } from "@/features/auth/hooks/useAuth";
import { LogoutConfirmDialog } from "@/features/auth/components/LogoutConfirmDialog";

interface NavbarProps {
  onToggleSidebar: () => void;
  className?: string;
}

export function Navbar({ onToggleSidebar, className }: NavbarProps) {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const [showLogoutDialog, setShowLogoutDialog] = useState(false);

  const handleLogout = async () => {
    await logout();
    setShowLogoutDialog(false);
    navigate("/login", { replace: true });
  };

  return (
    <>
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
          <img src="/logo.png" alt="" className="h-11 w-11 object-contain" />
          <span className="hidden sm:inline font-bold">
            <span className="text-foreground">Preply </span>
            <span className="text-blue-600 dark:text-blue-500">AI</span>
          </span>
        </Link>

        {/* Spacer */}
        <div className="flex-1" />

        {/* Theme toggle + Auth */}
        <nav className="flex items-center gap-2">
          <ThemeToggle />
          {isAuthenticated ? (
            <>
              <div className="hidden sm:flex items-center gap-2 text-sm text-foreground">
                <User className="h-4 w-4" />
                <span>{user?.fullName || user?.email}</span>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowLogoutDialog(true)}
                aria-label="Sign out"
              >
                <LogOut className="mr-2 h-4 w-4" />
                <span className="hidden sm:inline">Sign Out</span>
              </Button>
            </>
          ) : (
            <>
              <Button variant="ghost" size="sm" asChild>
                <Link to="/register">
                  <UserPlus className="mr-2 h-4 w-4" />
                  Register
                </Link>
              </Button>
              <Button variant="default" size="sm" asChild>
                <Link to="/login">
                  <LogIn className="mr-2 h-4 w-4" />
                  Sign In
                </Link>
              </Button>
            </>
          )}
        </nav>
      </header>

      <LogoutConfirmDialog
        open={showLogoutDialog}
        onOpenChange={setShowLogoutDialog}
        onConfirm={handleLogout}
      />
    </>
  );
}
