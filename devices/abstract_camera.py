from abc import ABC, abstractmethod
from typing import Iterator

from models.camera import Frame

class AbstractCamera(ABC):
    """Abstract base class for all cameras."""

    @abstractmethod
    def connect(self) -> None:
        """Connect to the camera."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the camera."""
        pass

    @abstractmethod
    def capture_frame(self) -> Frame:
        """Capture a single frame from the camera."""
        pass

    @abstractmethod
    def trigger_capture(self) -> None:
        """Trigger a non-blocking frame capture."""
        pass

    @abstractmethod
    def collect_frame(self) -> Frame:
        """Collect the frame after triggering capture."""
        pass

    @abstractmethod
    def stream(self) -> Iterator[Frame]:
        """Stream frames from the camera."""
        pass

    @abstractmethod
    def check_connection(self) -> bool:
        """Check the camera's connection status."""
        pass

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if the camera is connected."""
        pass

    @property
    @abstractmethod
    def camera_id(self) -> str:
        """Get the unique ID of the camera."""
        pass
