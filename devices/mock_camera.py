import time
import numpy as np
import threading
from typing import Iterator
from devices.abstract_camera import AbstractCamera
from models.camera import Frame
import cv2

class MockCamera(AbstractCamera):
    """A mock camera for testing purposes with enhanced simulation capabilities."""

    def __init__(self, camera_id: str, model: str = "D435i"):
        self._camera_id = camera_id
        self._model = model
        self._is_connected = False
        self._resolution = self._get_resolution()
        self._capture_event = threading.Event()
        self._last_frame = None

    def _get_resolution(self) -> tuple:
        """Get resolution based on camera model."""
        if "ZED" in self._model:
            return (2208, 1242)  # ZED 2i resolution
        return (1280, 720)  # Default D435i resolution

    def _generate_mock_image(self) -> np.ndarray:
        """Generate mock image with camera model and ID overlay."""
        height, width = self._resolution
        # Create gradient background
        img = np.zeros((height, width, 3), dtype=np.uint8)
        for i in range(3):
            img[:, :, i] = np.linspace(0, 255, width, dtype=np.uint8)
        
        # Add camera info text
        text = f"{self._model} ({self._camera_id})"
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, text, (50, height//2), font, 1, (255, 255, 255), 2, cv2.LINE_AA)
        return img

    def connect(self) -> None:
        """Simulate connecting to the camera."""
        print(f"Connecting to mock camera: {self._camera_id} ({self._model})")
        self._is_connected = True

    def disconnect(self) -> None:
        """Simulate disconnecting from the camera."""
        print(f"Disconnecting from mock camera: {self._camera_id}")
        self._is_connected = False

    def capture_frame(self) -> Frame:
        """Simulate capturing a single frame with mock image."""
        if not self._is_connected:
            raise ConnectionError(f"Camera {self._camera_id} is not connected.")
        
        return Frame(
            camera_id=self._camera_id,
            sequence_id=int(time.time()),
            timestamp_ns=time.time_ns(),
            rgb_image=self._generate_mock_image(),
            depth_image=np.random.randint(0, 1000, self._resolution, dtype=np.uint16),
        )

    def trigger_capture(self) -> None:
        """Simulate triggering a capture."""
        if not self._is_connected:
            return
        self._capture_event.clear()
        # In a real scenario, this would trigger the hardware.
        # For the mock, we'll just generate a frame and store it.
        self._last_frame = self.capture_frame()
        self._capture_event.set()

    def collect_frame(self) -> Frame:
        """Collect the captured frame."""
        if not self._is_connected:
            raise ConnectionError(f"Camera {self._camera_id} is not connected.")
        
        # Wait for the capture event to be set
        self._capture_event.wait(timeout=1.0)  # 1-second timeout
        if not self._capture_event.is_set():
            raise TimeoutError(f"Frame collection timed out for {self.camera_id}")
        
        return self._last_frame

    def check_connection(self) -> bool:
        """For mock camera, we just return the current status."""
        return self._is_connected

    def stream(self) -> Iterator[Frame]:
        """Simulate streaming frames."""
        while self._is_connected:
            yield self.capture_frame()
            time.sleep(1 / 30)  # Simulate 30 FPS

    @property
    def is_connected(self) -> bool:
        """Check if the camera is connected."""
        return self._is_connected

    @property
    def camera_id(self) -> str:
        """Get the unique ID of the camera."""
        return self._camera_id

    @property
    def model(self) -> str:
        """Get the camera model."""
        return self._model
