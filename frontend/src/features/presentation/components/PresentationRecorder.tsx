import { useRef, useEffect } from "react";
import {
  Loader2,
  Video,
  Square,
  CheckCircle2,
} from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { useVideoRecorder } from "../hooks/useVideoRecorder";
import { useMediaPipeFaceMesh } from "../hooks/useMediaPipeFaceMesh";
import type { SessionMetrics } from "../hooks/useMediaPipeFaceMesh";
import { EyeGazeOverlay } from "./EyeGazeOverlay";
import { RecordingWarnings, useRecordingWarnings } from "./RecordingWarnings";

interface PresentationRecorderProps {
  sessionId: string;
  durationSeconds: number;
  onRecordingComplete: (blob: Blob, duration: number, metrics?: SessionMetrics) => void;
  onTimerExpired: () => void;
  onMaterialsSelected: (file: File) => void;
  isUploading: boolean;
  materialsUploaded: boolean;
}

export function PresentationRecorder({
  sessionId: _sessionId,
  durationSeconds,
  onRecordingComplete,
  onTimerExpired,
  onMaterialsSelected: _onMaterialsSelected,
  isUploading: _isUploading,
  materialsUploaded: _materialsUploaded,
}: PresentationRecorderProps) {
  const videoPreviewRef = useRef<HTMLVideoElement>(null);
  const canvasOverlayRef = useRef<HTMLCanvasElement>(null);

  const {
    status,
    videoBlob,
    error,
    duration,
    previewUrl,
    startRecording,
    stopRecording,
    getStream,
  } = useVideoRecorder();

  const {
    warnings: recordingWarnings,
    addWarning,
    dismissWarning,
    removeByType,
  } = useRecordingWarnings();

  // MediaPipe Face Mesh — real face detection with landmarks
  const { faceStatus, currentWarnings, getSessionMetrics } = useMediaPipeFaceMesh({
    videoRef: videoPreviewRef,
    canvasRef: canvasOverlayRef,
    isActive: status === "recording",
  });

  // Sync MediaPipe warnings to the RecordingWarnings component
  useEffect(() => {
    if (status !== "recording") return;

    // Face detection warnings
    if (faceStatus === "not-detected") {
      addWarning("face-not-detected", "Face not detected. Please ensure your face is visible.");
    } else {
      removeByType("face-not-detected");
    }

    // Position/lighting warnings from MediaPipe
    const hasLightingWarning = currentWarnings.some((w) => w.includes("lighting"));
    if (hasLightingWarning) {
      addWarning("low-lighting", "Low lighting — improve lighting for better tracking.");
    } else {
      removeByType("low-lighting");
    }
  }, [faceStatus, currentWarnings, status, addWarning, removeByType]);

  // Connect live stream to video element for preview
  useEffect(() => {
    if (status === "recording" && videoPreviewRef.current) {
      const stream = getStream();
      if (stream) {
        videoPreviewRef.current.srcObject = stream;
        videoPreviewRef.current.play().catch(() => {});
      }
    }
  }, [status, getStream]);

  // Notify parent when recording completes (include session metrics)
  useEffect(() => {
    if (status === "stopped" && videoBlob) {
      const metrics = getSessionMetrics();
      onRecordingComplete(videoBlob, duration, metrics);
    }
  }, [status, videoBlob, duration, onRecordingComplete, getSessionMetrics]);

  // Auto-stop recording when user-chosen duration expires
  useEffect(() => {
    if (status === "recording" && duration >= durationSeconds) {
      stopRecording();
      onTimerExpired();
    }
  }, [status, duration, durationSeconds, stopRecording, onTimerExpired]);

  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="space-y-2">
        <h2 className="text-xl font-bold">Recording Session</h2>
        <p className="text-muted-foreground">
          Record your presentation. Your camera and microphone will be used.
        </p>
      </div>

      {/* Error display */}
      {error && (
        <div
          className="rounded-md bg-destructive/10 border border-destructive/20 p-3 text-sm text-destructive"
          role="alert"
        >
          {error}
        </div>
      )}

      {/* Video Preview Area */}
      <div className="relative overflow-hidden rounded-lg border border-border bg-black aspect-video">
        {status === "recording" && (
          <>
            <video
              ref={videoPreviewRef}
              autoPlay
              muted
              playsInline
              className="h-full w-full object-cover"
              aria-label="Live camera preview"
            />
            {/* Canvas overlay for face detection outline */}
            <canvas
              ref={canvasOverlayRef}
              className="absolute inset-0 h-full w-full pointer-events-none"
              aria-hidden="true"
            />
          </>
        )}

        {status === "stopped" && previewUrl && (
          <video
            src={previewUrl}
            controls
            className="h-full w-full object-cover"
            aria-label="Recorded video playback"
          />
        )}

        {(status === "idle" || status === "requesting") && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center text-white/70">
              <Video className="mx-auto h-12 w-12 mb-2" />
              <p className="text-sm">
                {status === "requesting"
                  ? "Requesting camera access..."
                  : "Click Start Recording to begin"}
              </p>
              <p className="mt-2 text-lg font-bold text-white/90">
                {formatDuration(durationSeconds)}
              </p>
              <p className="text-xs text-white/50">session duration</p>
            </div>
          </div>
        )}

        {/* Recording indicator with countdown timer */}
        {status === "recording" && (
          <>
            {/* Timer showing elapsed / chosen duration */}
            <div className="absolute top-4 left-4 flex items-center gap-2 rounded-full bg-red-600/90 px-3 py-1">
              <div className="h-2 w-2 animate-pulse rounded-full bg-white" />
              <span className="text-xs font-medium text-white">
                {formatDuration(duration)} / {formatDuration(durationSeconds)}
              </span>
            </div>
            {/* Warning when under 1 minute left */}
            {durationSeconds - duration <= 60 && durationSeconds - duration > 0 && (
              <div className="absolute top-4 right-4 flex items-center gap-1.5 rounded-full bg-yellow-500/90 px-3 py-1">
                <span className="text-xs font-medium text-white">
                  ⚠ {formatDuration(durationSeconds - duration)} left
                </span>
              </div>
            )}

            {/* Eye Gaze Overlay */}
            <EyeGazeOverlay faceStatus={faceStatus} />

            {/* Recording Warnings (lighting/face detection) */}
            <RecordingWarnings warnings={recordingWarnings} onDismiss={dismissWarning} />
          </>
        )}
      </div>

      {/* Countdown progress bar — always visible during session */}
      {(status === "idle" || status === "recording" || status === "error") && (
        <div className="space-y-1">
          <div className="h-3 w-full overflow-hidden rounded-full bg-secondary">
            <div
              className={`h-full rounded-full transition-all duration-1000 ${
                status !== "recording"
                  ? "bg-green-500"
                  : (durationSeconds - duration) / durationSeconds <= 0.1
                    ? "bg-red-500"
                    : (durationSeconds - duration) / durationSeconds <= 0.5
                      ? "bg-yellow-500"
                      : "bg-green-500"
              }`}
              style={{
                width: status === "recording"
                  ? `${Math.max(0, ((durationSeconds - duration) / durationSeconds) * 100)}%`
                  : "100%",
              }}
              role="progressbar"
              aria-valuenow={status === "recording" ? durationSeconds - duration : durationSeconds}
              aria-valuemin={0}
              aria-valuemax={durationSeconds}
              aria-label={`Time remaining: ${formatDuration(status === "recording" ? durationSeconds - duration : durationSeconds)}`}
            />
          </div>
          <p className="text-center text-sm font-medium text-foreground">
            {status === "recording"
              ? `⏱ ${formatDuration(durationSeconds - duration)} remaining`
              : `⏱ ${formatDuration(durationSeconds)} session`}
          </p>
        </div>
      )}

      {/* Recording Controls */}
      <div className="flex flex-col items-center gap-2">
        <div className="flex items-center justify-center gap-4">
          {(status === "idle" || status === "error") && (
            <Button onClick={startRecording} size="lg">
              <Video className="mr-2 h-4 w-4" />
              Start Recording
            </Button>
          )}

          {status === "requesting" && (
            <Button disabled size="lg">
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Requesting Access...
            </Button>
          )}

          {status === "recording" && (
            <Button onClick={stopRecording} variant="destructive" size="lg">
              <Square className="mr-2 h-4 w-4" />
              Stop Recording
            </Button>
          )}

          {status === "stopped" && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <CheckCircle2 className="h-4 w-4 text-green-600" />
              <span>Recording complete — {formatDuration(duration)}</span>
            </div>
          )}
        </div>

        {/* Duration info */}
        {(status === "idle" || status === "error" || status === "recording") && (
          <p className="text-xs text-muted-foreground">
            Session duration: {Math.floor(durationSeconds / 60)} minute{Math.floor(durationSeconds / 60) !== 1 ? "s" : ""}
            {status === "recording" ? " — recording will auto-save when time is up" : ""}
          </p>
        )}
      </div>
    </div>
  );
}
