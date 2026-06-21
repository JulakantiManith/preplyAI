"""Unit tests for MediaPipeClient eye contact and head pose analysis.

Tests cover:
- Eye contact percentage calculation (Property 22)
- Head pose stability classification (Property 23)
- Error handling for empty inputs
- Gaze classification logic

Requirements: 13.1, 13.2, 13.3, 13.4, 13.5
"""

import pytest

from app.integrations.mediapipe_client import (
    EyeContactResult,
    GazeDirection,
    HeadPoseMeasurement,
    HeadPoseResult,
    MediaPipeClient,
    MediaPipeClientError,
    StabilityClassification,
)


@pytest.fixture
def client() -> MediaPipeClient:
    """Create a MediaPipeClient instance with default thresholds."""
    return MediaPipeClient()


@pytest.fixture
def custom_client() -> MediaPipeClient:
    """Create a MediaPipeClient with custom thresholds for testing."""
    return MediaPipeClient(gaze_threshold=0.3, stability_threshold=3.0)


class TestEyeContactPercentage:
    """Tests for eye contact percentage calculation (Requirement 13.2, Property 22)."""

    def test_all_camera_frames(self, client: MediaPipeClient) -> None:
        """100% eye contact when all frames are camera."""
        frames = [GazeDirection.CAMERA] * 10
        result = client.calculate_eye_contact_percentage(frames)
        assert result == 100.0

    def test_no_camera_frames(self, client: MediaPipeClient) -> None:
        """0% eye contact when all frames are away."""
        frames = [GazeDirection.AWAY] * 10
        result = client.calculate_eye_contact_percentage(frames)
        assert result == 0.0

    def test_half_camera_frames(self, client: MediaPipeClient) -> None:
        """50% eye contact when half frames are camera."""
        frames = [GazeDirection.CAMERA] * 5 + [GazeDirection.AWAY] * 5
        result = client.calculate_eye_contact_percentage(frames)
        assert result == 50.0

    def test_one_third_camera_frames(self, client: MediaPipeClient) -> None:
        """33.3% eye contact (rounded to 1 decimal)."""
        frames = [GazeDirection.CAMERA] * 1 + [GazeDirection.AWAY] * 2
        result = client.calculate_eye_contact_percentage(frames)
        assert result == 33.3

    def test_two_thirds_camera_frames(self, client: MediaPipeClient) -> None:
        """66.7% eye contact (rounded to 1 decimal)."""
        frames = [GazeDirection.CAMERA] * 2 + [GazeDirection.AWAY] * 1
        result = client.calculate_eye_contact_percentage(frames)
        assert result == 66.7

    def test_single_camera_frame(self, client: MediaPipeClient) -> None:
        """Single frame that is camera = 100%."""
        frames = [GazeDirection.CAMERA]
        result = client.calculate_eye_contact_percentage(frames)
        assert result == 100.0

    def test_single_away_frame(self, client: MediaPipeClient) -> None:
        """Single frame that is away = 0%."""
        frames = [GazeDirection.AWAY]
        result = client.calculate_eye_contact_percentage(frames)
        assert result == 0.0

    def test_empty_frames_raises_error(self, client: MediaPipeClient) -> None:
        """Empty frame list raises MediaPipeClientError."""
        with pytest.raises(MediaPipeClientError):
            client.calculate_eye_contact_percentage([])

    def test_result_rounded_to_one_decimal(self, client: MediaPipeClient) -> None:
        """Result is rounded to exactly 1 decimal place."""
        # 1/7 = 14.285714... should round to 14.3
        frames = [GazeDirection.CAMERA] * 1 + [GazeDirection.AWAY] * 6
        result = client.calculate_eye_contact_percentage(frames)
        assert result == 14.3

    def test_formula_camera_frames_div_total_times_100(
        self, client: MediaPipeClient
    ) -> None:
        """Verify formula: (camera_frames / total_frames) × 100."""
        camera_count = 7
        total_count = 13
        frames = [GazeDirection.CAMERA] * camera_count + [GazeDirection.AWAY] * (
            total_count - camera_count
        )
        result = client.calculate_eye_contact_percentage(frames)
        expected = round((camera_count / total_count) * 100, 1)
        assert result == expected


class TestAnalyzeEyeContact:
    """Tests for the analyze_eye_contact method."""

    def test_returns_eye_contact_result(self, client: MediaPipeClient) -> None:
        """Returns proper EyeContactResult model."""
        frames = [GazeDirection.CAMERA] * 3 + [GazeDirection.AWAY] * 7
        result = client.analyze_eye_contact(frames)
        assert isinstance(result, EyeContactResult)
        assert result.total_frames == 10
        assert result.camera_frames == 3
        assert result.eye_contact_percentage == 30.0
        assert len(result.frame_classifications) == 10

    def test_empty_frames_raises_error(self, client: MediaPipeClient) -> None:
        """Empty frame list raises error."""
        with pytest.raises(MediaPipeClientError):
            client.analyze_eye_contact([])


class TestHeadPoseStabilityClassification:
    """Tests for head pose stability classification (Requirement 13.4, Property 23)."""

    def test_stable_when_low_variation(self, client: MediaPipeClient) -> None:
        """Stable when all axes have std dev below threshold."""
        measurements = [
            HeadPoseMeasurement(pitch=1.0, yaw=0.5, roll=-0.5),
            HeadPoseMeasurement(pitch=1.2, yaw=0.6, roll=-0.4),
            HeadPoseMeasurement(pitch=0.8, yaw=0.4, roll=-0.6),
            HeadPoseMeasurement(pitch=1.1, yaw=0.5, roll=-0.5),
        ]
        result = client.classify_head_stability(measurements)
        assert result == StabilityClassification.STABLE

    def test_excessive_when_pitch_exceeds_threshold(
        self, client: MediaPipeClient
    ) -> None:
        """Excessive when pitch std dev exceeds threshold."""
        measurements = [
            HeadPoseMeasurement(pitch=-20.0, yaw=0.0, roll=0.0),
            HeadPoseMeasurement(pitch=20.0, yaw=0.0, roll=0.0),
            HeadPoseMeasurement(pitch=-20.0, yaw=0.0, roll=0.0),
            HeadPoseMeasurement(pitch=20.0, yaw=0.0, roll=0.0),
        ]
        result = client.classify_head_stability(measurements)
        assert result == StabilityClassification.EXCESSIVE

    def test_excessive_when_yaw_exceeds_threshold(
        self, client: MediaPipeClient
    ) -> None:
        """Excessive when yaw std dev exceeds threshold."""
        measurements = [
            HeadPoseMeasurement(pitch=0.0, yaw=-20.0, roll=0.0),
            HeadPoseMeasurement(pitch=0.0, yaw=20.0, roll=0.0),
            HeadPoseMeasurement(pitch=0.0, yaw=-20.0, roll=0.0),
            HeadPoseMeasurement(pitch=0.0, yaw=20.0, roll=0.0),
        ]
        result = client.classify_head_stability(measurements)
        assert result == StabilityClassification.EXCESSIVE

    def test_excessive_when_roll_exceeds_threshold(
        self, client: MediaPipeClient
    ) -> None:
        """Excessive when roll std dev exceeds threshold."""
        measurements = [
            HeadPoseMeasurement(pitch=0.0, yaw=0.0, roll=-20.0),
            HeadPoseMeasurement(pitch=0.0, yaw=0.0, roll=20.0),
            HeadPoseMeasurement(pitch=0.0, yaw=0.0, roll=-20.0),
            HeadPoseMeasurement(pitch=0.0, yaw=0.0, roll=20.0),
        ]
        result = client.classify_head_stability(measurements)
        assert result == StabilityClassification.EXCESSIVE

    def test_single_measurement_is_stable(self, client: MediaPipeClient) -> None:
        """Single measurement is always stable (no variation)."""
        measurements = [HeadPoseMeasurement(pitch=10.0, yaw=15.0, roll=5.0)]
        result = client.classify_head_stability(measurements)
        assert result == StabilityClassification.STABLE

    def test_empty_measurements_raises_error(self, client: MediaPipeClient) -> None:
        """Empty measurement list raises error."""
        with pytest.raises(MediaPipeClientError):
            client.classify_head_stability([])

    def test_custom_threshold_affects_classification(
        self, custom_client: MediaPipeClient
    ) -> None:
        """Custom threshold (3.0) classifies moderate movement as excessive."""
        # These have std dev ~4.0 per axis - exceeds custom threshold of 3.0
        measurements = [
            HeadPoseMeasurement(pitch=-4.0, yaw=0.0, roll=0.0),
            HeadPoseMeasurement(pitch=4.0, yaw=0.0, roll=0.0),
            HeadPoseMeasurement(pitch=-4.0, yaw=0.0, roll=0.0),
            HeadPoseMeasurement(pitch=4.0, yaw=0.0, roll=0.0),
        ]
        result = custom_client.classify_head_stability(measurements)
        assert result == StabilityClassification.EXCESSIVE

    def test_identical_measurements_stable(self, client: MediaPipeClient) -> None:
        """Identical measurements have zero std dev → stable."""
        measurements = [
            HeadPoseMeasurement(pitch=5.0, yaw=3.0, roll=1.0),
            HeadPoseMeasurement(pitch=5.0, yaw=3.0, roll=1.0),
            HeadPoseMeasurement(pitch=5.0, yaw=3.0, roll=1.0),
        ]
        result = client.classify_head_stability(measurements)
        assert result == StabilityClassification.STABLE


class TestAnalyzeHeadPose:
    """Tests for the analyze_head_pose aggregate method."""

    def test_returns_head_pose_result(self, client: MediaPipeClient) -> None:
        """Returns proper HeadPoseResult model with aggregated stats."""
        measurements = [
            HeadPoseMeasurement(pitch=2.0, yaw=1.0, roll=-1.0),
            HeadPoseMeasurement(pitch=4.0, yaw=3.0, roll=-3.0),
        ]
        result = client.analyze_head_pose(measurements)
        assert isinstance(result, HeadPoseResult)
        assert result.avg_pitch == 3.0
        assert result.avg_yaw == 2.0
        assert result.avg_roll == -2.0
        assert result.stability == StabilityClassification.STABLE

    def test_empty_measurements_raises_error(self, client: MediaPipeClient) -> None:
        """Empty measurements raises error."""
        with pytest.raises(MediaPipeClientError):
            client.analyze_head_pose([])

    def test_std_values_computed(self, client: MediaPipeClient) -> None:
        """Standard deviation values are computed and present."""
        measurements = [
            HeadPoseMeasurement(pitch=0.0, yaw=0.0, roll=0.0),
            HeadPoseMeasurement(pitch=10.0, yaw=10.0, roll=10.0),
        ]
        result = client.analyze_head_pose(measurements)
        assert result.std_pitch == 5.0
        assert result.std_yaw == 5.0
        assert result.std_roll == 5.0


class TestGazeClassification:
    """Tests for iris-based gaze classification logic."""

    def test_centered_iris_is_camera(self, client: MediaPipeClient) -> None:
        """Iris at center of eye → looking at camera."""

        class MockLandmark:
            def __init__(self, x: float, y: float):
                self.x = x
                self.y = y

        # Create landmarks where iris is centered between corners
        landmarks = [None] * 478
        # Left eye: outer corner at x=0.3, inner corner at x=0.4, iris at center (0.35)
        landmarks[LEFT_EYE_OUTER_CORNER] = MockLandmark(0.3, 0.5)
        landmarks[LEFT_EYE_INNER_CORNER] = MockLandmark(0.4, 0.5)
        landmarks[LEFT_IRIS_CENTER] = MockLandmark(0.35, 0.5)
        # Right eye: outer corner at x=0.7, inner corner at x=0.6, iris at center (0.65)
        landmarks[RIGHT_EYE_OUTER_CORNER] = MockLandmark(0.7, 0.5)
        landmarks[RIGHT_EYE_INNER_CORNER] = MockLandmark(0.6, 0.5)
        landmarks[RIGHT_IRIS_CENTER] = MockLandmark(0.65, 0.5)

        result = client.classify_gaze(landmarks, 640, 480)
        assert result == GazeDirection.CAMERA

    def test_displaced_iris_is_away(self, client: MediaPipeClient) -> None:
        """Iris at edge of eye → looking away."""

        class MockLandmark:
            def __init__(self, x: float, y: float):
                self.x = x
                self.y = y

        landmarks = [None] * 478
        # Left eye: iris at outer corner (max displacement)
        landmarks[LEFT_EYE_OUTER_CORNER] = MockLandmark(0.3, 0.5)
        landmarks[LEFT_EYE_INNER_CORNER] = MockLandmark(0.4, 0.5)
        landmarks[LEFT_IRIS_CENTER] = MockLandmark(0.3, 0.5)  # At outer corner
        # Right eye: iris at outer corner
        landmarks[RIGHT_EYE_OUTER_CORNER] = MockLandmark(0.7, 0.5)
        landmarks[RIGHT_EYE_INNER_CORNER] = MockLandmark(0.6, 0.5)
        landmarks[RIGHT_IRIS_CENTER] = MockLandmark(0.7, 0.5)  # At outer corner

        result = client.classify_gaze(landmarks, 640, 480)
        assert result == GazeDirection.AWAY


class TestLowLightingDetection:
    """Tests for low lighting detection (Requirement 13.5)."""

    def test_dark_frame_detected(self, client: MediaPipeClient) -> None:
        """Very dark frame is detected as low lighting."""
        import numpy as np

        # Create a very dark frame (mean brightness ~10)
        dark_frame = np.full((480, 640, 3), 10, dtype=np.uint8)
        assert client._is_low_lighting(dark_frame) is True

    def test_bright_frame_not_detected(self, client: MediaPipeClient) -> None:
        """Normal brightness frame is not flagged."""
        import numpy as np

        # Create a normally lit frame (mean brightness ~128)
        bright_frame = np.full((480, 640, 3), 128, dtype=np.uint8)
        assert client._is_low_lighting(bright_frame) is False

    def test_borderline_dark_frame(self, client: MediaPipeClient) -> None:
        """Frame exactly at threshold boundary."""
        import numpy as np

        # Frame at exactly 40 mean brightness (threshold)
        borderline_frame = np.full((480, 640, 3), 40, dtype=np.uint8)
        assert client._is_low_lighting(borderline_frame) is False

    def test_below_threshold_frame(self, client: MediaPipeClient) -> None:
        """Frame just below threshold is flagged."""
        import numpy as np

        below_frame = np.full((480, 640, 3), 39, dtype=np.uint8)
        assert client._is_low_lighting(below_frame) is True


# Import landmark indices for test use
from app.integrations.mediapipe_client import (
    LEFT_EYE_INNER_CORNER,
    LEFT_EYE_OUTER_CORNER,
    LEFT_IRIS_CENTER,
    RIGHT_EYE_INNER_CORNER,
    RIGHT_EYE_OUTER_CORNER,
    RIGHT_IRIS_CENTER,
)
