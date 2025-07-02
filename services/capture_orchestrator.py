from typing import List
from models.camera import Frame
from services.device_manager import DeviceManager

class CaptureOrchestrator:
    """Orchestrates the capture of frames from all cameras."""

    def __init__(self, device_manager: DeviceManager):
        self._device_manager = device_manager

    def capture_all_frames(self) -> List[Frame]:
        """Capture a frame from each connected camera."""
        frames: List[Frame] = []
        for camera in self._device_manager.get_all_cameras():
            if camera.is_connected:
                try:
                    frame = camera.capture_frame()
                    frames.append(frame)
                except ConnectionError as e:
                    print(f"Error capturing frame from {camera.camera_id}: {e}")
        return frames
