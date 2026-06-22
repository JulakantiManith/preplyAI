import { Skeleton } from "@/shared/components/ui/skeleton";
import { cn } from "@/shared/lib/utils";

interface CardSkeletonProps {
  className?: string;
}

export function CardSkeleton({ className }: CardSkeletonProps) {
  return (
    <div
      className={cn(
        "rounded-lg border bg-card p-4 shadow-sm",
        className
      )}
      role="status"
      aria-label="Loading card"
    >
      <div className="flex items-center justify-between">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-8 w-8 rounded-lg" />
      </div>
      <div className="mt-3">
        <Skeleton className="h-7 w-16" />
        <Skeleton className="mt-2 h-3 w-32" />
      </div>
    </div>
  );
}

interface MetricsCardSkeletonProps {
  count?: number;
  className?: string;
}

export function MetricsCardsSkeleton({
  count = 5,
  className,
}: MetricsCardSkeletonProps) {
  return (
    <div
      className={cn("grid gap-4 sm:grid-cols-2 lg:grid-cols-5", className)}
      role="status"
      aria-label="Loading metrics"
    >
      {Array.from({ length: count }).map((_, i) => (
        <CardSkeleton key={i} />
      ))}
    </div>
  );
}
