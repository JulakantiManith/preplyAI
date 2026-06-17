import { Mic, MicOff, Square, AlertCircle } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { cn } from "@/shared/lib/utils";
import type { RecorderStatus } from "../hooks/useAudioRecorder";

interface AudioRecorderProps {
  status: RecorderStatus;
  duration: number;
  error: string | null;
  onStart: () => void;
  onStop: () => void;
  disabled?: boolean;
  className?: string;
}

function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
}

export function AudioRecorder({
  status,
  duration,
  error,
  onStart,
  onStop,
  disabled = false,
  className,
}: AudioRecorderProps) {
  const isRecording = status === "recording";

  return (
    <div className={cn("space-y-3", className)}>
      {/* Error message for microphone denial */}
      {error && (
        <div
          className="flex items-start gap-2 rounded-md bg-destructive/10 border border-destructive/20 p-3 text-sm text-destructive"
          role="alert"
        >
          <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
          <p>{error}</p>
        </div>
      )}

      <div className="flex items-center gap-4">
        {/* Record / Stop Button */}
        {isRecording ? (
          <Button
            type="button"
            variant="destructive"
            size="lg"
            onClick={onStop}
            aria-label="Stop recording"
            className="gap-2"
          >
            <Square className="h-4 w-4" />
            Stop Recording
          </Button>
        ) : status === "stopped" ? (
          /* After recording is stopped, don't show record button — only show duration */
          <div className="flex items-center gap-2 rounded-md border border-green-200 bg-green-50 dark:bg-green-900/20 dark:border-green-800 px-4 py-2">
            <Mic className="h-4 w-4 text-green-600 dark:text-green-400" />
            <span className="text-sm font-medium text-green-700 dark:text-green-300">
              Recording saved ({formatDuration(duration)})
            </span>
          </div>
        ) : (
          <Button
            type="button"
            variant="default"
            size="lg"
            onClick={onStart}
            disabled={disabled || status === "requesting"}
            aria-label="Start recording"
            className="gap-2"
          >
            {status === "error" ? (
              <MicOff className="h-4 w-4" />
            ) : (
              <Mic className="h-4 w-4" />
            )}
            {status === "requesting" ? "Requesting access..." : "Record Answer"}
          </Button>
        )}

        {/* Duration display while recording */}
        {isRecording && (
          <div className="flex items-center gap-2">
            <span
              className="h-3 w-3 rounded-full bg-destructive animate-pulse"
              aria-hidden="true"
            />
            <span
              className="font-mono text-sm text-muted-foreground"
              aria-live="polite"
              aria-label={`Recording duration: ${formatDuration(duration)}`}
            >
              {formatDuration(duration)}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
