import { Eye, Move3D, AlertTriangle, CheckCircle2 } from "lucide-react";
import type { VisualAnalysisResponse } from "../services/presentationService";

interface VisualAnalysisMetricsProps {
  visualAnalysis: VisualAnalysisResponse;
}

/**
 * Displays eye contact percentage and head movement stability metrics
 * in the session report after analysis is complete.
 *
 * Requirements: 13.2, 13.3, 13.4
 */
export function VisualAnalysisMetrics({ visualAnalysis }: VisualAnalysisMetricsProps) {
  const { eye_contact, head_pose, warnings } = visualAnalysis;

  const eyeContactColor = getScoreColor(eye_contact.eye_contact_percentage);
  const isStable = head_pose.stability === "stable";

  return (
    <div className="rounded-lg border border-border p-6 space-y-5">
      <div className="flex items-center gap-2">
        <Eye className="h-5 w-5 text-primary" />
        <h3 className="text-lg font-semibold">Visual Analysis</h3>
      </div>

      {/* Eye Contact Section */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-foreground">Eye Contact</span>
          <span className={`text-sm font-semibold ${eyeContactColor}`}>
            {eye_contact.eye_contact_percentage}%
          </span>
        </div>
        <div className="h-3 w-full overflow-hidden rounded-full bg-secondary">
          <div
            className={`h-full rounded-full transition-all duration-500 ${getBarColor(eye_contact.eye_contact_percentage)}`}
            style={{ width: `${Math.min(eye_contact.eye_contact_percentage, 100)}%` }}
            role="progressbar"
            aria-valuenow={eye_contact.eye_contact_percentage}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label={`Eye contact: ${eye_contact.eye_contact_percentage}%`}
          />
        </div>
        <p className="text-xs text-muted-foreground">
          {eye_contact.camera_frames} of {eye_contact.total_frames} frames looking at camera
        </p>
      </div>

      {/* Head Movement Stability Section */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5">
            <Move3D className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm font-medium text-foreground">Head Movement</span>
          </div>
          <div className="flex items-center gap-1.5">
            {isStable ? (
              <CheckCircle2 className="h-4 w-4 text-green-600 dark:text-green-400" />
            ) : (
              <AlertTriangle className="h-4 w-4 text-orange-500 dark:text-orange-400" />
            )}
            <span
              className={`text-sm font-semibold ${
                isStable
                  ? "text-green-600 dark:text-green-400"
                  : "text-orange-600 dark:text-orange-400"
              }`}
            >
              {isStable ? "Stable" : "Excessive Movement"}
            </span>
          </div>
        </div>

        {/* Head pose stats grid */}
        <div className="grid grid-cols-3 gap-3 rounded-md bg-muted/50 p-3">
          <PoseStat label="Pitch" avg={head_pose.avg_pitch} std={head_pose.std_pitch} />
          <PoseStat label="Yaw" avg={head_pose.avg_yaw} std={head_pose.std_yaw} />
          <PoseStat label="Roll" avg={head_pose.avg_roll} std={head_pose.std_roll} />
        </div>
      </div>

      {/* Session Warnings */}
      {warnings.length > 0 && (
        <div className="space-y-2">
          <span className="text-sm font-medium text-foreground">Session Warnings</span>
          <ul className="space-y-1">
            {warnings.map((warning, index) => (
              <li
                key={index}
                className="flex items-start gap-2 text-xs text-muted-foreground"
              >
                <AlertTriangle className="mt-0.5 h-3 w-3 shrink-0 text-yellow-500" />
                <span>{warning}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

interface PoseStatProps {
  label: string;
  avg: number;
  std: number;
}

function PoseStat({ label, avg, std }: PoseStatProps) {
  return (
    <div className="text-center">
      <p className="text-xs font-medium text-muted-foreground">{label}</p>
      <p className="text-sm font-semibold text-foreground">{avg.toFixed(1)}°</p>
      <p className="text-xs text-muted-foreground">±{std.toFixed(1)}°</p>
    </div>
  );
}

function getScoreColor(percentage: number): string {
  if (percentage >= 70) return "text-green-600 dark:text-green-400";
  if (percentage >= 50) return "text-yellow-600 dark:text-yellow-400";
  return "text-red-600 dark:text-red-400";
}

function getBarColor(percentage: number): string {
  if (percentage >= 70) return "bg-green-500 dark:bg-green-400";
  if (percentage >= 50) return "bg-yellow-500 dark:bg-yellow-400";
  return "bg-red-500 dark:bg-red-400";
}
