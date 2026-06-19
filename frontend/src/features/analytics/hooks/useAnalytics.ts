import { useQuery } from "@tanstack/react-query";
import {
  getAnalyticsProgress,
  getAnalyticsTrends,
} from "../services/analyticsService";
import type { TimeRange } from "../services/analyticsService";

const ANALYTICS_PROGRESS_KEY = "analytics-progress" as const;
const ANALYTICS_TRENDS_KEY = "analytics-trends" as const;

export function useAnalyticsProgress(timeRange: TimeRange) {
  return useQuery({
    queryKey: [ANALYTICS_PROGRESS_KEY, timeRange],
    queryFn: () => getAnalyticsProgress(timeRange),
  });
}

export function useAnalyticsTrends(timeRange: TimeRange) {
  return useQuery({
    queryKey: [ANALYTICS_TRENDS_KEY, timeRange],
    queryFn: () => getAnalyticsTrends(timeRange),
  });
}
