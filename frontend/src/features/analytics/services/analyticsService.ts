import apiClient from "@/shared/lib/axios";

// Time range type
export type TimeRange = "daily" | "weekly" | "monthly" | "3months" | "yearly";

// API response types (snake_case from backend)
interface ProgressDataPointApi {
  period: string;
  session_count: number;
  average_score: number | null;
}

interface AnalyticsProgressApiResponse {
  has_sessions: boolean;
  has_enough_data: boolean;
  data_points: ProgressDataPointApi[];
}

interface ScoreTrendApi {
  date: string;
  average_score: number;
  session_count: number;
}

interface AnalyticsTrendsApiResponse {
  has_sessions: boolean;
  has_enough_data: boolean;
  trends: {
    overall_scores: ScoreTrendApi[];
    confidence_scores: ScoreTrendApi[];
    communication_scores: ScoreTrendApi[];
  };
}

// Frontend types (camelCase)
export interface ProgressDataPoint {
  period: string;
  sessionCount: number;
  averageScore: number | null;
}

export interface AnalyticsProgressData {
  hasSessions: boolean;
  hasEnoughData: boolean;
  dataPoints: ProgressDataPoint[];
}

export interface ScoreTrend {
  date: string;
  averageScore: number;
  sessionCount: number;
}

export interface AnalyticsTrends {
  overallScores: ScoreTrend[];
  confidenceScores: ScoreTrend[];
  communicationScores: ScoreTrend[];
}

export interface AnalyticsTrendsData {
  hasSessions: boolean;
  hasEnoughData: boolean;
  trends: AnalyticsTrends;
}

// Mapper functions
function mapProgressDataPoints(data: ProgressDataPointApi[]): ProgressDataPoint[] {
  return data.map((item) => ({
    period: item.period,
    sessionCount: item.session_count,
    averageScore: item.average_score,
  }));
}

function mapProgressResponse(data: AnalyticsProgressApiResponse): AnalyticsProgressData {
  return {
    hasSessions: data.has_sessions,
    hasEnoughData: data.has_enough_data,
    dataPoints: mapProgressDataPoints(data.data_points),
  };
}

function mapScoreTrends(data: ScoreTrendApi[]): ScoreTrend[] {
  return data.map((item) => ({
    date: item.date,
    averageScore: item.average_score,
    sessionCount: item.session_count,
  }));
}

function mapTrendsResponse(data: AnalyticsTrendsApiResponse): AnalyticsTrendsData {
  return {
    hasSessions: data.has_sessions,
    hasEnoughData: data.has_enough_data,
    trends: {
      overallScores: mapScoreTrends(data.trends.overall_scores),
      confidenceScores: mapScoreTrends(data.trends.confidence_scores),
      communicationScores: mapScoreTrends(data.trends.communication_scores),
    },
  };
}

// API functions
export async function getAnalyticsProgress(timeRange: TimeRange): Promise<AnalyticsProgressData> {
  const response = await apiClient.get<AnalyticsProgressApiResponse>(
    "/analytics/progress",
    { params: { time_range: timeRange } }
  );
  return mapProgressResponse(response.data);
}

export async function getAnalyticsTrends(timeRange: TimeRange): Promise<AnalyticsTrendsData> {
  const response = await apiClient.get<AnalyticsTrendsApiResponse>(
    "/analytics/trends",
    { params: { time_range: timeRange } }
  );
  return mapTrendsResponse(response.data);
}
