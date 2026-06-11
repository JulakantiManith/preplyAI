import { X, LayoutDashboard, Mic, Presentation, BarChart3, Clock, UserCircle } from "lucide-react";
import { NavLink } from "react-router-dom";
import { cn } from "@/shared/lib/utils";

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  className?: string;
}

const navItems = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/interview", label: "Interview", icon: Mic },
  { to: "/presentation", label: "Presentation", icon: Presentation },
  { to: "/analytics", label: "Analytics", icon: BarChart3 },
  { to: "/history", label: "History", icon: Clock },
  { to: "/profile", label: "Profile", icon: UserCircle },
] as const;

export function Sidebar({ isOpen, onClose, className }: SidebarProps) {
  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 md:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r bg-background transition-transform duration-200 ease-in-out md:static md:translate-x-0 md:z-auto",
          isOpen ? "translate-x-0" : "-translate-x-full",
          className
        )}
      >
        {/* Mobile close button */}
        <div className="flex h-16 items-center justify-between border-b px-4 md:hidden">
          <span className="font-semibold">Navigation</span>
          <button
            onClick={onClose}
            className="rounded-md p-2 hover:bg-accent transition-colors"
            aria-label="Close sidebar"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation links */}
        <nav className="flex-1 space-y-1 p-4" aria-label="Main navigation">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              onClick={onClose}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-primary/10 text-primary"
                    : "text-muted-foreground hover:bg-accent hover:text-foreground"
                )
              }
            >
              <item.icon className="h-5 w-5 shrink-0" />
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>
    </>
  );
}
