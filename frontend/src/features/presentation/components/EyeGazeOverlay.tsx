import { ScanFace, EyeOff, RotateCcw, Loader2 } from "lucide-react";
import type { FaceStatus } from "../hooks/useMediaPipeFaceMesh";

interface EyeGazeOverlayProps {
  faceStatus: FaceStatus;
}

/**
 * Real-time overlay showing face detection and orientation status.
 *
 * Four states:
 * - "loading" (blue): MediaPipe model is loading
 * - "facing-camera" (green): face detected, facing camera
 * - "turned-away" (amber): face detected but turned away
 * - "not-detected" (red): no face visible
 *
 * Requirements: 13.1, 13.5
 */
export function EyeGazeOverlay({ faceStatus }: EyeGazeOverlayProps) {
  const config = STATUS_CONFIG[faceStatus];

  return (
    <div
      className="absolute bottom-4 left-4 flex items-center gap-2 rounded-full px-3 py-1.5 text-xs font-medium shadow-md backdrop-blur-sm"
      style={{ backgroundColor: config.bgColor }}
      aria-live="polite"
      aria-label={config.ariaLabel}
    >
      <config.Icon className="h-3.5 w-3.5 text-white" />
      <span className="text-white">{config.label}</span>
      {faceStatus === "facing-camera" && (
        <span className="relative flex h-2 w-2">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-white opacity-75" />
          <span className="relative inline-flex h-2 w-2 rounded-full bg-white" />
        </span>
      )}
      {faceStatus === "loading" && (
        <Loader2 className="h-3 w-3 animate-spin text-white" />
      )}
    </div>
  );
}

const STATUS_CONFIG = {
  loading: {
    bgColor: "rgba(59, 130, 246, 0.85)",
    label: "Loading Face Mesh...",
    ariaLabel: "Loading MediaPipe face detection model",
    Icon: Loader2,
  },
  "facing-camera": {
    bgColor: "rgba(34, 197, 94, 0.85)",
    label: "Face Detected",
    ariaLabel: "Face detected — gaze tracking active",
    Icon: ScanFace,
  },
  "turned-away": {
    bgColor: "rgba(245, 158, 11, 0.85)",
    label: "Please Face Camera",
    ariaLabel: "Face turned away — please look at the camera",
    Icon: RotateCcw,
  },
  "not-detected": {
    bgColor: "rgba(239, 68, 68, 0.85)",
    label: "No Face Detected",
    ariaLabel: "No face detected — ensure face is visible",
    Icon: EyeOff,
  },
} as const;
