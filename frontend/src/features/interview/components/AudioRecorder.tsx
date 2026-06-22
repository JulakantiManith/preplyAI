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

function WaveformBars() {
  return (
    <div className="flex items-center gap-[3px] h-8" aria-hidden="true">
      {Array.from({ length: 12 }).map((_, i) => (
        <div
          key={i}
          className="w-[3px] rounded-full bg-destructive/80 dark:bg-destructive-foreground/80"
          style={{
            animation: `waveform 1.2s ease-in-out infinite`,
            animationDelay: `${i * 0.1}s`,
            height: "100%",
          }}
        />
      ))}
    </div>
  );
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
          className="flex items-start gap-2 rounded-lg bg-destructive/10 border border-destructive/20 p-3 text-sm text-destructive animate-in fade-in slide-in-from-top-1 duration-200"
          role="alert"
        >
          <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
          <p>{error}</p>
        </div>
      )}

      <div
        className={cn(
          "rounded-xl border-2 p-5 transition-all duration-300",
          isRecording
            ? "border-destructive/50 bg-destructive/5 dark:bg-destructive/10 shadow-sm shadow-destructive/10"
            : status === "stopped"
              ? "border-green-300 dark:border-green-700 bg-green-50/50 dark:bg-green-900/10"
              : "border-input bg-background"
        )}
      >
        <div className="flex items-center gap-4">
          {/* Record / Stop Button */}
          {isRecording ? (
            <Button
              type="button"
              variant="destructive"
              size="lg"
              onClick={onStop}
              aria-label="Stop recording"
              className="gap-2 shadow-md transition-transform duration-200 hover:scale-105"
            >
              <Square className="h-4 w-4" />
              Stop
            </Button>
          ) : status === "stopped" ? (
            <div className="flex items-center gap-2 rounded-lg border border-green-200 dark:border-green-700 bg-green-50 dark:bg-green-900/20 px-4 py-2.5 animate-in fade-in duration-300">
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
              className="gap-2 shadow-sm transition-transform duration-200 hover:scale-105"
            >
              {status === "error" ? (
                <MicOff className="h-4 w-4" />
              ) : (
                <Mic className="h-4 w-4" />
              )}
              {status === "requesting" ? "Requesting access..." : "Record Answer"}
            </Button>
          )}

          {/* Waveform and duration while recording */}
          {isRecording && (
            <div className="flex items-center gap-3 flex-1 animate-in fade-in duration-300">
              <WaveformBars />
              <div className="flex items-center gap-2 ml-auto">
                <span
                  className="h-2.5 w-2.5 rounded-full bg-destructive animate-pulse"
                  aria-hidden="true"
                />
                <span
                  className="font-mono text-sm font-medium text-foreground tabular-nums"
                  aria-live="polite"
                  aria-label={`Recording duration: ${formatDuration(duration)}`}
                >
                  {formatDuration(duration)}
                </span>
              </div>
            </div>
          )}

          {/* Idle hint */}
          {status === "idle" && (
            <p className="text-xs text-muted-foreground animate-in fade-in duration-300">
              Click to start recording your answer
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
