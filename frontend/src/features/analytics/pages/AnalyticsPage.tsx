import { useState } from "react";
import { BarChart3, Info } from "lucide-react";
import { useAnalyticsProgress, useAnalyticsTrends } from "../hooks/useAnalytics";
import { TimeRangeSelector } from "../components/TimeRangeSelector";
import { ScoreTrendChart } from "../components/ScoreTrendChart";
import { SessionFrequencyChart } from "../components/SessionFrequencyChart";
import { MetricBreakdown } from "../components/MetricBreakdown";
import { LoadingSpinner } from "@/shared/components/LoadingSpinner";
import { ErrorMessage } from "@/shared/components/ErrorMessage";
import type { TimeRange } from "../services/analyticsService";

export function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState<TimeRange>("weekly");

  const {
    data: progressData,
    isLoading: progressLoading,
    isError: progressError,
    error: progressErr,
    refetch: refetchProgress,
  } = useAnalyticsProgress(timeRange);

  const {
    data: trendsData,
    isLoading: trendsLoading,
    isError: trendsError,
    error: trendsErr,
    refetch: refetchTrends,
  } = useAnalyticsTrends(timeRange);

  const isLoading = progressLoading || trendsLoading;
  const isError = progressError || trendsError;

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <LoadingSpinner label="Loading analytics..." />
      </div>
    );
  }

  if (isError) {
    const errorMessage =
      progressErr instanceof Error
        ? progressErr.message
        : trendsErr instanceof Error
          ? trendsErr.message
          : "Failed to load analytics data.";

    return (
      <ErrorMessage
        message={errorMessage}
        retry={() => {
          void refetchProgress();
          void refetchTrends();
        }}
      />
    );
  }

  if (!progressData || !trendsData) {
    return null;
  }

  const hasEnoughData = progressData.hasEnoughData && trendsData.hasEnoughData;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-2">
          <BarChart3 className="h-6 w-6 text-primary" />
          <h1 className="text-2xl font-bold">Analytics</h1>
        </div>
        <TimeRangeSelector value={timeRange} onChange={setTimeRange} />
      </div>

      {!hasEnoughData && (
        <div className="flex items-start gap-3 rounded-lg border border-blue-200 bg-blue-50 p-4 dark:border-blue-800 dark:bg-blue-950/30">
          <Info className="mt-0.5 h-5 w-5 shrink-0 text-blue-600 dark:text-blue-400" />
          <div>
            <p className="text-sm font-medium text-blue-800 dark:text-blue-200">
              Keep practicing to unlock full trend analysis
            </p>
            <p className="mt-1 text-sm text-blue-600 dark:text-blue-400">
              Complete at least 3 sessions to see detailed score trends and comprehensive analytics. You're doing great — keep going!
            </p>
          </div>
        </div>
      )}

      <MetricBreakdown
        overallScores={trendsData.trends.overallScores}
        confidenceScores={trendsData.trends.confidenceScores}
        communicationScores={trendsData.trends.communicationScores}
      />

      <div className="grid gap-6 lg:grid-cols-2">
        <ScoreTrendChart
          overallScores={trendsData.trends.overallScores}
          confidenceScores={trendsData.trends.confidenceScores}
          communicationScores={trendsData.trends.communicationScores}
        />
        <SessionFrequencyChart dataPoints={progressData.dataPoints} />
      </div>
    </div>
  );
}
