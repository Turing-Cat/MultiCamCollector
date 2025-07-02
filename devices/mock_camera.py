import time
import numpy as np
from typing import Iterator
from devices.abstract_camera import AbstractCamera
from models.camera import Frame

class MockCamera(AbstractCamera):
    """A mock camera for testing purposes."""

    def __init__(self, camera_id: str):
        self._camera_id = camera_id
        self._is_connected = False

    def connect(self) -> None:
        """Simulate connecting to the camera."""
        print(f"Connecting to mock camera: {self._camera_id}")
        self._is_connected = True

    def disconnect(self) -> None:
        """Simulate disconnecting from the camera."""
        print(f"Disconnecting from mock camera: {self._camera_id}")
        self._is_connected = False

    def capture_frame(self) -> Frame:
        """Simulate capturing a single frame."""
        if not self._is_connected:
            raise ConnectionError(f"Camera {self._camera_id} is not connected.")
        
        return Frame(
            camera_id=self._camera_id,
            sequence_id=int(time.time()),
            timestamp_ns=time.time_ns(),
            rgb_image=np.random.randint(0, 256, (720, 1280, 3), dtype=np.uint8),
            depth_image=np.random.randint(0, 1000, (720, 1280), dtype=np.uint16),
        )

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
