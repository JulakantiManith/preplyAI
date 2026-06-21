import { useState, useCallback } from "react";
import { AlertTriangle, X, Sun, UserX } from "lucide-react";

export type RecordingWarningType = "low-lighting" | "face-not-detected";

interface RecordingWarning {
  id: string;
  type: RecordingWarningType;
  message: string;
}

interface RecordingWarningsProps {
  warnings: RecordingWarning[];
  onDismiss: (id: string) => void;
}

const ICON_MAP: Record<RecordingWarningType, typeof AlertTriangle> = {
  "low-lighting": Sun,
  "face-not-detected": UserX,
};

const COLOR_MAP: Record<RecordingWarningType, string> = {
  "low-lighting":
    "border-yellow-300 bg-yellow-50 text-yellow-800 dark:border-yellow-700 dark:bg-yellow-950 dark:text-yellow-200",
  "face-not-detected":
    "border-red-300 bg-red-50 text-red-800 dark:border-red-700 dark:bg-red-950 dark:text-red-200",
};

/**
 * Displays non-blocking, dismissible warning banners during recording.
 * Shows warnings for low lighting or face not detected conditions.
 *
 * Requirements: 13.5
 */
export function RecordingWarnings({ warnings, onDismiss }: RecordingWarningsProps) {
  if (warnings.length === 0) {
    return null;
  }

  return (
    <div className="absolute top-14 left-4 right-4 z-10 flex flex-col gap-2" role="alert">
      {warnings.map((warning) => {
        const Icon = ICON_MAP[warning.type];
        const colorClass = COLOR_MAP[warning.type];

        return (
          <div
            key={warning.id}
            className={`flex items-center gap-2 rounded-md border px-3 py-2 text-xs font-medium shadow-sm ${colorClass}`}
          >
            <Icon className="h-4 w-4 shrink-0" />
            <span className="flex-1">{warning.message}</span>
            <button
              onClick={() => onDismiss(warning.id)}
              className="shrink-0 rounded p-0.5 hover:opacity-70 transition-opacity"
              aria-label={`Dismiss warning: ${warning.message}`}
            >
              <X className="h-3.5 w-3.5" />
            </button>
          </div>
        );
      })}
    </div>
  );
}

/**
 * Hook for managing recording warnings state.
 * Provides methods to add, dismiss, and clear warnings.
 */
export function useRecordingWarnings() {
  const [warnings, setWarnings] = useState<RecordingWarning[]>([]);

  const addWarning = useCallback((type: RecordingWarningType, message: string) => {
    const id = `${type}-${Date.now()}`;
    setWarnings((prev) => {
      // Avoid duplicates of the same type
      if (prev.some((w) => w.type === type)) {
        return prev;
      }
      return [...prev, { id, type, message }];
    });
  }, []);

  const dismissWarning = useCallback((id: string) => {
    setWarnings((prev) => prev.filter((w) => w.id !== id));
  }, []);

  const clearWarnings = useCallback(() => {
    setWarnings([]);
  }, []);

  const removeByType = useCallback((type: RecordingWarningType) => {
    setWarnings((prev) => prev.filter((w) => w.type !== type));
  }, []);

  return {
    warnings,
    addWarning,
    dismissWarning,
    clearWarnings,
    removeByType,
  };
}
