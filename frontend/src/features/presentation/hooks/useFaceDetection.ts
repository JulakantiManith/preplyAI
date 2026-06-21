/**
 * Re-exports from the MediaPipe Face Mesh hook.
 * This file maintains backward compatibility for components that import from here.
 */
export { useMediaPipeFaceMesh as useFaceDetection } from "./useMediaPipeFaceMesh";
export type { FaceStatus, SessionMetrics } from "./useMediaPipeFaceMesh";
