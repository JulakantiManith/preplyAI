"""MediaPipe integration client for eye contact and head pose analysis.

Provides face mesh detection, eye gaze classification, and head pose
estimation using Google's MediaPipe framework. Designed for processing
video frames from interview/presentation practice sessions.

Key capabilities:
- Eye gaze direction classification (camera vs. away)
- Eye contact percentage calculation over a session
- Head pose estimation (pitch, yaw, roll)
- Head movement stability classification

Requirements: 13.1, 13.2, 13.3, 13.4, 13.5
"""

import logging
import math
from enum import Enum
from typing import Optional

import numpy as np
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# MediaPipe Face Mesh landmark indices for eye gaze estimation
# Left eye iris center and eye corners
LEFT_IRIS_CENTER = 468
LEFT_EYE_INNER_CORNER = 133
LEFT_EYE_OUTER_CORNER = 33

# Right eye iris center and eye corners
RIGHT_IRIS_CENTER = 473
RIGHT_EYE_INNER_CORNER = 362
RIGHT_EYE_OUTER_CORNER = 263

# Face model points for head pose estimation (nose tip, chin, eye corners, mouth corners)
NOSE_TIP = 1
CHIN = 199
LEFT_EYE_LEFT_CORNER = 33
RIGHT_EYE_RIGHT_CORNER = 263
LEFT_MOUTH_CORNER = 61
RIGHT_MOUTH_CORNER = 291

# Default thresholds
DEFAULT_GAZE_THRESHOLD = 0.25  # iris displacement ratio for "looking at camera"
DEFAULT_STABILITY_THRESHOLD = 5.0  # degrees standard deviation per axis


class GazeDirection(str, Enum):
    """Classification of gaze direction for a single frame."""

    CAMERA = "camera"
    AWAY = "away"


class StabilityClassification(str, Enum):
    """Head movement stability classification."""

    STABLE = "stable"
    EXCESSIVE = "excessive"


class MediaPipeClientError(Exception):
    """Raised when MediaPipe processing fails."""

    pass


class FaceNotDetectedError(MediaPipeClientError):
    """Raised when no face is detected in the frame."""

    pass


class LowLightingError(MediaPipeClientError):
    """Raised when lighting conditions are too poor for detection."""

    pass


class HeadPoseMeasurement(BaseModel):
    """A single head pose measurement (pitch, yaw, roll in degrees)."""

    pitch: float = Field(description="Vertical head rotation in degrees")
    yaw: float = Field(description="Horizontal head rotation in degrees")
    roll: float = Field(description="Tilting head rotation in degrees")


class HeadPoseResult(BaseModel):
    """Result of head pose analysis over a session."""

    measurements: list[HeadPoseMeasurement] = Field(
        description="All head pose measurements"
    )
    avg_pitch: float = Field(description="Average pitch in degrees")
    avg_yaw: float = Field(description="Average yaw in degrees")
    avg_roll: float = Field(description="Average roll in degrees")
    std_pitch: float = Field(description="Standard deviation of pitch")
    std_yaw: float = Field(description="Standard deviation of yaw")
    std_roll: float = Field(description="Standard deviation of roll")
    stability: StabilityClassification = Field(
        description="Overall stability classification"
    )


class EyeContactResult(BaseModel):
    """Result of eye contact analysis over a session."""

    total_frames: int = Field(ge=0, description="Total frames analyzed")
    camera_frames: int = Field(ge=0, description="Frames with gaze at camera")
    eye_contact_percentage: float = Field(
        ge=0.0, le=100.0, description="Percentage of eye contact, rounded to 1 decimal"
    )
    frame_classifications: list[GazeDirection] = Field(
        description="Per-frame gaze classification"
    )


class VisualAnalysisResult(BaseModel):
    """Combined result of eye contact and head pose analysis."""

    eye_contact: EyeContactResult
    head_pose: HeadPoseResult
    warnings: list[str] = Field(default_factory=list)


class MediaPipeClient:
    """Client for MediaPipe face mesh analysis with gaze and pose detection.

    Provides:
    - Frame-by-frame gaze direction classification
    - Eye contact percentage over a session
    - Head pose estimation (pitch, yaw, roll)
    - Head movement stability classification

    Requirements: 13.1, 13.2, 13.3, 13.4, 13.5
    """

    def __init__(
        self,
        gaze_threshold: float = DEFAULT_GAZE_THRESHOLD,
        stability_threshold: float = DEFAULT_STABILITY_THRESHOLD,
    ) -> None:
        """Initialize MediaPipe client with configurable thresholds.

        Args:
            gaze_threshold: Maximum iris displacement ratio to classify as
                looking at camera. Lower = stricter. Default 0.25.
            stability_threshold: Maximum standard deviation (degrees) per axis
                for "stable" classification. Default 5.0.
        """
        self._gaze_threshold = gaze_threshold
        self._stability_threshold = stability_threshold
        self._face_mesh = None
        logger.info(
            "MediaPipeClient initialized (gaze_threshold=%.2f, stability_threshold=%.1f)",
            gaze_threshold,
            stability_threshold,
        )

    def _get_face_mesh(self):
        """Lazily initialize MediaPipe FaceMesh.

        Returns:
            MediaPipe FaceMesh solution instance.
        """
        if self._face_mesh is None:
            import mediapipe as mp

            self._face_mesh = mp.solutions.face_mesh.FaceMesh(
                static_image_mode=False,
                max_num_faces=1,
                refine_landmarks=True,  # Enables iris landmarks (468-477)
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
            )
        return self._face_mesh

    def classify_gaze(
        self, landmarks: list, image_width: int, image_height: int
    ) -> GazeDirection:
        """Classify gaze direction from face mesh landmarks.

        Computes iris position relative to eye corners. If the iris is
        near the center of the eye opening, the user is looking at camera.

        Args:
            landmarks: MediaPipe face mesh landmarks (478 points with iris).
            image_width: Frame width in pixels.
            image_height: Frame height in pixels.

        Returns:
            GazeDirection.CAMERA if looking at camera, AWAY otherwise.
        """
        # Get left eye iris ratio
        left_ratio = self._compute_iris_ratio(
            landmarks,
            LEFT_IRIS_CENTER,
            LEFT_EYE_INNER_CORNER,
            LEFT_EYE_OUTER_CORNER,
            image_width,
        )

        # Get right eye iris ratio
        right_ratio = self._compute_iris_ratio(
            landmarks,
            RIGHT_IRIS_CENTER,
            RIGHT_EYE_INNER_CORNER,
            RIGHT_EYE_OUTER_CORNER,
            image_width,
        )

        # Average displacement from center for both eyes
        avg_displacement = (left_ratio + right_ratio) / 2.0

        if avg_displacement <= self._gaze_threshold:
            return GazeDirection.CAMERA
        return GazeDirection.AWAY

    def _compute_iris_ratio(
        self,
        landmarks: list,
        iris_idx: int,
        inner_corner_idx: int,
        outer_corner_idx: int,
        image_width: int,
    ) -> float:
        """Compute normalized iris displacement from eye center.

        Returns a value between 0.0 (centered) and 0.5 (at edge).

        Args:
            landmarks: Face mesh landmarks.
            iris_idx: Landmark index for iris center.
            inner_corner_idx: Landmark index for inner eye corner.
            outer_corner_idx: Landmark index for outer eye corner.
            image_width: Frame width for denormalization.

        Returns:
            Normalized displacement (0.0 = center, 0.5 = corner).
        """
        iris = landmarks[iris_idx]
        inner = landmarks[inner_corner_idx]
        outer = landmarks[outer_corner_idx]

        # Horizontal positions in pixel space
        iris_x = iris.x * image_width
        inner_x = inner.x * image_width
        outer_x = outer.x * image_width

        # Eye width and center
        eye_width = abs(outer_x - inner_x)
        if eye_width < 1.0:
            return 0.5  # Eye too small to detect, consider as "away"

        eye_center_x = (inner_x + outer_x) / 2.0
        displacement = abs(iris_x - eye_center_x) / eye_width

        return displacement

    def estimate_head_pose(
        self, landmarks: list, image_width: int, image_height: int
    ) -> HeadPoseMeasurement:
        """Estimate head pose (pitch, yaw, roll) from face landmarks.

        Uses a simplified geometric approach based on key facial landmark
        positions to estimate 3D head orientation.

        Args:
            landmarks: MediaPipe face mesh landmarks.
            image_width: Frame width in pixels.
            image_height: Frame height in pixels.

        Returns:
            HeadPoseMeasurement with pitch, yaw, roll in degrees.
        """
        # 3D model points (generic face model)
        model_points = np.array(
            [
                [0.0, 0.0, 0.0],  # Nose tip
                [0.0, -330.0, -65.0],  # Chin
                [-225.0, 170.0, -135.0],  # Left eye left corner
                [225.0, 170.0, -135.0],  # Right eye right corner
                [-150.0, -150.0, -125.0],  # Left mouth corner
                [150.0, -150.0, -125.0],  # Right mouth corner
            ],
            dtype=np.float64,
        )

        # 2D image points from landmarks
        landmark_indices = [
            NOSE_TIP,
            CHIN,
            LEFT_EYE_LEFT_CORNER,
            RIGHT_EYE_RIGHT_CORNER,
            LEFT_MOUTH_CORNER,
            RIGHT_MOUTH_CORNER,
        ]

        image_points = np.array(
            [
                [
                    landmarks[idx].x * image_width,
                    landmarks[idx].y * image_height,
                ]
                for idx in landmark_indices
            ],
            dtype=np.float64,
        )

        # Camera internals (approximate)
        focal_length = image_width
        center = (image_width / 2.0, image_height / 2.0)
        camera_matrix = np.array(
            [
                [focal_length, 0, center[0]],
                [0, focal_length, center[1]],
                [0, 0, 1],
            ],
            dtype=np.float64,
        )
        dist_coeffs = np.zeros((4, 1), dtype=np.float64)

        # Solve PnP
        import cv2

        success, rotation_vector, _ = cv2.solvePnP(
            model_points,
            image_points,
            camera_matrix,
            dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE,
        )

        if not success:
            logger.warning("solvePnP failed, returning zero pose")
            return HeadPoseMeasurement(pitch=0.0, yaw=0.0, roll=0.0)

        # Convert rotation vector to euler angles
        rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
        pitch, yaw, roll = self._rotation_matrix_to_euler(rotation_matrix)

        return HeadPoseMeasurement(
            pitch=round(pitch, 2),
            yaw=round(yaw, 2),
            roll=round(roll, 2),
        )

    def _rotation_matrix_to_euler(self, rotation_matrix: np.ndarray) -> tuple[float, float, float]:
        """Convert a 3x3 rotation matrix to Euler angles (pitch, yaw, roll).

        Args:
            rotation_matrix: 3x3 rotation matrix.

        Returns:
            Tuple of (pitch, yaw, roll) in degrees.
        """
        sy = math.sqrt(
            rotation_matrix[0, 0] ** 2 + rotation_matrix[1, 0] ** 2
        )
        singular = sy < 1e-6

        if not singular:
            pitch = math.atan2(rotation_matrix[2, 1], rotation_matrix[2, 2])
            yaw = math.atan2(-rotation_matrix[2, 0], sy)
            roll = math.atan2(rotation_matrix[1, 0], rotation_matrix[0, 0])
        else:
            pitch = math.atan2(-rotation_matrix[1, 2], rotation_matrix[1, 1])
            yaw = math.atan2(-rotation_matrix[2, 0], sy)
            roll = 0.0

        # Convert to degrees
        return (
            math.degrees(pitch),
            math.degrees(yaw),
            math.degrees(roll),
        )

    def calculate_eye_contact_percentage(
        self, frame_classifications: list[GazeDirection]
    ) -> float:
        """Calculate eye contact percentage from frame classifications.

        Formula: (camera_frames / total_frames) × 100, rounded to 1 decimal.

        Args:
            frame_classifications: List of gaze direction per frame.

        Returns:
            Eye contact percentage (0.0 to 100.0), rounded to 1 decimal.

        Raises:
            MediaPipeClientError: If no frames provided.
        """
        if not frame_classifications:
            raise MediaPipeClientError(
                "Cannot calculate eye contact percentage with no frames"
            )

        total_frames = len(frame_classifications)
        camera_frames = sum(
            1 for f in frame_classifications if f == GazeDirection.CAMERA
        )

        percentage = (camera_frames / total_frames) * 100
        return round(percentage, 1)

    def classify_head_stability(
        self, measurements: list[HeadPoseMeasurement]
    ) -> StabilityClassification:
        """Classify head movement stability from pose measurements.

        Stable: standard deviation of each axis (pitch, yaw, roll) is
        below the configured threshold.
        Excessive: any axis exceeds the threshold.

        Args:
            measurements: List of head pose measurements.

        Returns:
            StabilityClassification.STABLE or EXCESSIVE.

        Raises:
            MediaPipeClientError: If no measurements provided.
        """
        if not measurements:
            raise MediaPipeClientError(
                "Cannot classify stability with no measurements"
            )

        if len(measurements) == 1:
            return StabilityClassification.STABLE

        pitches = [m.pitch for m in measurements]
        yaws = [m.yaw for m in measurements]
        rolls = [m.roll for m in measurements]

        std_pitch = float(np.std(pitches, ddof=0))
        std_yaw = float(np.std(yaws, ddof=0))
        std_roll = float(np.std(rolls, ddof=0))

        if (
            std_pitch > self._stability_threshold
            or std_yaw > self._stability_threshold
            or std_roll > self._stability_threshold
        ):
            return StabilityClassification.EXCESSIVE

        return StabilityClassification.STABLE

    def analyze_head_pose(
        self, measurements: list[HeadPoseMeasurement]
    ) -> HeadPoseResult:
        """Analyze a sequence of head pose measurements.

        Computes aggregate statistics and stability classification.

        Args:
            measurements: List of head pose measurements from frames.

        Returns:
            HeadPoseResult with statistics and stability classification.

        Raises:
            MediaPipeClientError: If no measurements provided.
        """
        if not measurements:
            raise MediaPipeClientError("Cannot analyze empty measurements list")

        pitches = [m.pitch for m in measurements]
        yaws = [m.yaw for m in measurements]
        rolls = [m.roll for m in measurements]

        stability = self.classify_head_stability(measurements)

        return HeadPoseResult(
            measurements=measurements,
            avg_pitch=round(float(np.mean(pitches)), 2),
            avg_yaw=round(float(np.mean(yaws)), 2),
            avg_roll=round(float(np.mean(rolls)), 2),
            std_pitch=round(float(np.std(pitches, ddof=0)), 2),
            std_yaw=round(float(np.std(yaws, ddof=0)), 2),
            std_roll=round(float(np.std(rolls, ddof=0)), 2),
            stability=stability,
        )

    def analyze_eye_contact(
        self, frame_classifications: list[GazeDirection]
    ) -> EyeContactResult:
        """Analyze eye contact from a sequence of gaze classifications.

        Args:
            frame_classifications: Per-frame gaze direction list.

        Returns:
            EyeContactResult with percentage and statistics.

        Raises:
            MediaPipeClientError: If no frames provided.
        """
        if not frame_classifications:
            raise MediaPipeClientError("Cannot analyze empty frame list")

        total_frames = len(frame_classifications)
        camera_frames = sum(
            1 for f in frame_classifications if f == GazeDirection.CAMERA
        )
        percentage = round((camera_frames / total_frames) * 100, 1)

        return EyeContactResult(
            total_frames=total_frames,
            camera_frames=camera_frames,
            eye_contact_percentage=percentage,
            frame_classifications=frame_classifications,
        )

    def process_frame(
        self, frame: np.ndarray
    ) -> tuple[Optional[GazeDirection], Optional[HeadPoseMeasurement], list[str]]:
        """Process a single video frame for gaze and head pose.

        Args:
            frame: BGR image frame (numpy array from OpenCV).

        Returns:
            Tuple of (gaze_direction, head_pose, warnings).
            gaze_direction and head_pose are None if face not detected.
            warnings contain any issues (low lighting, face not found).

        Raises:
            LowLightingError: If frame is too dark for reliable detection.
            FaceNotDetectedError: If no face is found in the frame.
        """
        import cv2

        warnings: list[str] = []

        # Check lighting conditions
        if self._is_low_lighting(frame):
            warnings.append(
                "Low lighting detected. Please improve lighting or "
                "adjust camera positioning for better results."
            )
            raise LowLightingError(
                "Frame is too dark for reliable face detection. "
                "Please improve lighting conditions."
            )

        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image_height, image_width = frame.shape[:2]

        face_mesh = self._get_face_mesh()
        results = face_mesh.process(rgb_frame)

        if not results.multi_face_landmarks:
            warnings.append(
                "Face not detected. Please ensure your face is visible "
                "to the camera and improve lighting if needed."
            )
            raise FaceNotDetectedError(
                "No face detected in frame. Ensure face is visible to camera."
            )

        landmarks = results.multi_face_landmarks[0].landmark

        # Classify gaze
        gaze = self.classify_gaze(landmarks, image_width, image_height)

        # Estimate head pose
        head_pose = self.estimate_head_pose(landmarks, image_width, image_height)

        return gaze, head_pose, warnings

    def _is_low_lighting(self, frame: np.ndarray) -> bool:
        """Check if a frame has insufficient lighting.

        Uses average brightness of the frame. Threshold is set at
        a mean pixel value below 40 (out of 255).

        Args:
            frame: BGR image frame.

        Returns:
            True if lighting is too low for reliable detection.
        """
        import cv2

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mean_brightness = float(np.mean(gray))
        return mean_brightness < 40.0

    def analyze_session_frames(
        self, frames: list[np.ndarray]
    ) -> VisualAnalysisResult:
        """Analyze all frames from a video session.

        Processes each frame for gaze and head pose, aggregating results.
        Frames where face is not detected are skipped with warnings.

        Args:
            frames: List of BGR image frames from the session video.

        Returns:
            VisualAnalysisResult with eye contact and head pose data.

        Raises:
            MediaPipeClientError: If no frames could be processed.
        """
        gaze_classifications: list[GazeDirection] = []
        pose_measurements: list[HeadPoseMeasurement] = []
        all_warnings: list[str] = []

        for i, frame in enumerate(frames):
            try:
                gaze, pose, warnings = self.process_frame(frame)
                if gaze is not None:
                    gaze_classifications.append(gaze)
                if pose is not None:
                    pose_measurements.append(pose)
                all_warnings.extend(warnings)
            except (FaceNotDetectedError, LowLightingError) as e:
                logger.debug("Frame %d skipped: %s", i, str(e))
                all_warnings.append(str(e))

        if not gaze_classifications:
            raise MediaPipeClientError(
                "No frames could be processed. Ensure face is visible "
                "and lighting is adequate."
            )

        eye_contact = self.analyze_eye_contact(gaze_classifications)
        head_pose = self.analyze_head_pose(pose_measurements)

        # Deduplicate warnings
        unique_warnings = list(dict.fromkeys(all_warnings))

        logger.info(
            "Session analysis complete: %d/%d frames processed, "
            "eye contact=%.1f%%, stability=%s",
            len(gaze_classifications),
            len(frames),
            eye_contact.eye_contact_percentage,
            head_pose.stability.value,
        )

        return VisualAnalysisResult(
            eye_contact=eye_contact,
            head_pose=head_pose,
            warnings=unique_warnings,
        )
