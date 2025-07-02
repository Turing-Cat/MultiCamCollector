from typing import List
from devices.abstract_camera import AbstractCamera

class DeviceManager:
    """Manages the discovery and status of connected cameras."""

    def __init__(self):
        self._cameras: List[AbstractCamera] = []

    def discover_cameras(self) -> None:
        """Discover and connect to all available cameras."""
        # In a real implementation, this would use the SDKs to find devices.
        # For now, we'll use mock cameras.
        from devices.mock_camera import MockCamera

        self._cameras = [
            MockCamera(camera_id="D435i_1"),
            MockCamera(camera_id="D435i_2"),
            MockCamera(camera_id="D435i_3"),
            MockCamera(camera_id="D435i_4"),
            MockCamera(camera_id="ZED2i_1"),
        ]
        for camera in self._cameras:
            camera.connect()

    def get_all_cameras(self) -> List[AbstractCamera]:
        """Get a list of all discovered cameras."""
        return self._cameras

    def get_camera_by_id(self, camera_id: str) -> AbstractCamera:
        """Get a camera by its ID."""
        for camera in self._cameras:
            if camera.camera_id == camera_id:
                return camera
        raise ValueError(f"Camera with ID {camera_id} not found.")
