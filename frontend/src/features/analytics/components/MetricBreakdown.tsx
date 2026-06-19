import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import type { ScoreTrend } from "../services/analyticsService";

interface MetricBreakdownProps {
  overallScores: ScoreTrend[];
  confidenceScores: ScoreTrend[];
  communicationScores: ScoreTrend[];
}

interface MetricCardProps {
  label: string;
  scores: ScoreTrend[];
  color: string;
}

function computeLatestScore(scores: ScoreTrend[]): number | null {
  if (scores.length === 0) return null;
  return scores[scores.length - 1].averageScore;
}

function computeTrend(scores: ScoreTrend[]): "up" | "down" | "neutral" {
  if (scores.length < 2) return "neutral";
  const latest = scores[scores.length - 1].averageScore;
  const previous = scores[scores.length - 2].averageScore;
  const diff = latest - previous;
  if (diff > 2) return "up";
  if (diff < -2) return "down";
  return "neutral";
}

function computeAverage(scores: ScoreTrend[]): number | null {
  if (scores.length === 0) return null;
  const sum = scores.reduce((acc, s) => acc + s.averageScore, 0);
  return Math.round(sum / scores.length);
}

function MetricCard({ label, scores, color }: MetricCardProps) {
  const latest = computeLatestScore(scores);
  const trend = computeTrend(scores);
  const average = computeAverage(scores);

  return (
    <div className="rounded-lg border bg-card p-4 shadow-sm">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-medium text-muted-foreground">{label}</h4>
        {trend === "up" && <TrendingUp className="h-4 w-4 text-green-500" />}
        {trend === "down" && <TrendingDown className="h-4 w-4 text-red-500" />}
        {trend === "neutral" && <Minus className="h-4 w-4 text-muted-foreground" />}
      </div>
      <div className="mt-2 flex items-baseline gap-2">
        <span className="text-2xl font-bold" style={{ color }}>
          {latest !== null ? `${Math.round(latest)}%` : "—"}
        </span>
        {average !== null && (
          <span className="text-xs text-muted-foreground">
            avg {average}%
          </span>
        )}
      </div>
      <p className="mt-1 text-xs text-muted-foreground">
        {scores.length} data {scores.length === 1 ? "point" : "points"}
      </p>
    </div>
  );
}

export function MetricBreakdown({
  overallScores,
  confidenceScores,
  communicationScores,
}: MetricBreakdownProps) {
  return (
    <div className="rounded-lg border bg-card p-6 shadow-sm">
      <h3 className="text-lg font-semibold">Score Breakdown</h3>
      <p className="mt-1 text-sm text-muted-foreground">
        Latest scores and trends for each category
      </p>
      <div className="mt-4 grid gap-4 sm:grid-cols-3">
        <MetricCard
          label="Overall Score"
          scores={overallScores}
          color="#3b82f6"
        />
        <MetricCard
          label="Confidence"
          scores={confidenceScores}
          color="#10b981"
        />
        <MetricCard
          label="Communication"
          scores={communicationScores}
          color="#f59e0b"
        />
      </div>
    </div>
  );
}
