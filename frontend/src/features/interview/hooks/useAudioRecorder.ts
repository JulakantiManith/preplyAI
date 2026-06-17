import { useState, useRef, useCallback } from "react";

export type RecorderStatus = "idle" | "requesting" | "recording" | "stopped" | "error";

interface AudioRecorderState {
  status: RecorderStatus;
  audioBlob: Blob | null;
  error: string | null;
  duration: number;
}

export function useAudioRecorder() {
  const [state, setState] = useState<AudioRecorderState>({
    status: "idle",
    audioBlob: null,
    error: null,
    duration: 0,
  });

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const startTimeRef = useRef<number>(0);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const getMimeType = (): string => {
    if (MediaRecorder.isTypeSupported("audio/webm;codecs=opus")) {
      return "audio/webm;codecs=opus";
    }
    if (MediaRecorder.isTypeSupported("audio/webm")) {
      return "audio/webm";
    }
    if (MediaRecorder.isTypeSupported("audio/mp4")) {
      return "audio/mp4";
    }
    return "";
  };

  const startRecording = useCallback(async () => {
    setState((prev) => ({ ...prev, status: "requesting", error: null, audioBlob: null }));
    chunksRef.current = [];

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mimeType = getMimeType();

      const options: MediaRecorderOptions = {};
      if (mimeType) {
        options.mimeType = mimeType;
      }

      const mediaRecorder = new MediaRecorder(stream, options);
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, {
          type: mimeType || "audio/webm",
        });
        setState((prev) => ({
          ...prev,
          status: "stopped",
          audioBlob: blob,
        }));

        // Stop all tracks
        stream.getTracks().forEach((track) => track.stop());

        // Clear timer
        if (timerRef.current) {
          clearInterval(timerRef.current);
          timerRef.current = null;
        }
      };

      mediaRecorder.onerror = () => {
        setState((prev) => ({
          ...prev,
          status: "error",
          error: "Recording failed. Please try again.",
        }));
        stream.getTracks().forEach((track) => track.stop());
        if (timerRef.current) {
          clearInterval(timerRef.current);
          timerRef.current = null;
        }
      };

      mediaRecorder.start();
      startTimeRef.current = Date.now();

      // Update duration every second
      timerRef.current = setInterval(() => {
        setState((prev) => ({
          ...prev,
          duration: Math.floor((Date.now() - startTimeRef.current) / 1000),
        }));
      }, 1000);

      setState((prev) => ({ ...prev, status: "recording", duration: 0 }));
    } catch (err: unknown) {
      let errorMessage = "Could not access microphone.";

      if (err instanceof DOMException) {
        if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
          errorMessage =
            "Microphone access was denied. Please allow microphone access in your browser settings and try again.";
        } else if (err.name === "NotFoundError") {
          errorMessage =
            "No microphone found. Please connect a microphone and try again.";
        } else if (err.name === "NotReadableError") {
          errorMessage =
            "Microphone is already in use by another application. Please close other apps using the microphone and try again.";
        }
      }

      setState((prev) => ({
        ...prev,
        status: "error",
        error: errorMessage,
      }));
    }
  }, []);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
      mediaRecorderRef.current.stop();
    }
  }, []);

  const resetRecorder = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
      mediaRecorderRef.current.stop();
    }
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    chunksRef.current = [];
    setState({
      status: "idle",
      audioBlob: null,
      error: null,
      duration: 0,
    });
  }, []);

  return {
    ...state,
    startRecording,
    stopRecording,
    resetRecorder,
  };
}
