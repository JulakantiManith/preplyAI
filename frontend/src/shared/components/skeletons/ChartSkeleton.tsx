import { Skeleton } from "@/shared/components/ui/skeleton";
import { cn } from "@/shared/lib/utils";

interface ChartSkeletonProps {
  className?: string;
}

export function ChartSkeleton({ className }: ChartSkeletonProps) {
  return (
    <div
      className={cn("rounded-lg border bg-card p-6 shadow-sm", className)}
      role="status"
      aria-label="Loading chart"
    >
      <div className="flex items-center justify-between">
        <Skeleton className="h-6 w-36" />
        <Skeleton className="h-8 w-28 rounded-md" />
      </div>
      <div className="mt-6 flex items-end gap-2">
        {[40, 65, 50, 80, 55, 70, 45].map((height, i) => (
          <Skeleton
            key={i}
            className="flex-1 rounded-t-sm"
            style={{ height: `${height}%`, minHeight: `${height * 1.6}px` }}
          />
        ))}
      </div>
    </div>
  );
}
