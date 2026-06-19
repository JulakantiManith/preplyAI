import { ExternalLink } from "lucide-react";
import { cn } from "@/shared/lib/utils";

interface FooterProps {
  className?: string;
}

export function Footer({ className }: FooterProps) {
  const creatorName = import.meta.env.VITE_CREATOR_NAME || "Creator";
  const githubUrl = import.meta.env.VITE_GITHUB_URL || "#";
  const linkedinUrl = import.meta.env.VITE_LINKEDIN_URL || "#";
  const appName = import.meta.env.VITE_APP_NAME || "AI Interview & Presentation Coach";
  const currentYear = new Date().getFullYear();

  return (
    <footer
      className={cn(
        "border-t bg-background px-4 py-4 md:px-6",
        className
      )}
    >
      <div className="mx-auto flex flex-col items-center gap-3 sm:flex-row sm:justify-between">
        {/* Creator info and social links */}
        <div className="flex flex-col items-center gap-2 sm:flex-row sm:gap-3">
          <span className="text-sm text-muted-foreground">
            Created by {creatorName}
          </span>

          <div className="flex items-center gap-3">
            <a
              href={githubUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground"
              aria-label={`${creatorName}'s GitHub profile`}
            >
              <ExternalLink className="h-4 w-4" />
              <span>GitHub</span>
            </a>

            <a
              href={linkedinUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground"
              aria-label={`${creatorName}'s LinkedIn profile`}
            >
              <ExternalLink className="h-4 w-4" />
              <span>LinkedIn</span>
            </a>
          </div>
        </div>

        {/* Copyright */}
        <p className="text-sm text-muted-foreground">
          &copy; {currentYear} {appName}
        </p>
      </div>
    </footer>
  );
}
