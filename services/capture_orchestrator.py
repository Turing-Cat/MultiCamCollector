from typing import List
from models.camera import Frame
from services.device_manager import DeviceManager

class CaptureOrchestrator:
    """Orchestrates the capture of frames from all cameras."""

    def __init__(self, device_manager: DeviceManager):
        self._device_manager = device_manager

    def capture_all_frames(self) -> List[Frame]:
        """Capture a frame from each connected camera using a synchronized trigger."""
        frames: List[Frame] = []
        connected_cameras = [cam for cam in self._device_manager.get_all_cameras() if cam.is_connected]

        # 1. Trigger all cameras as quickly as possible
        for camera in connected_cameras:
            try:
                camera.trigger_capture()
            except Exception as e:
                print(f"Error triggering capture for {camera.camera_id}: {e}")

        # 2. Collect the frames from all cameras
        for camera in connected_cameras:
            try:
                frame = camera.collect_frame()
                if frame:
                    frames.append(frame)
            except (ConnectionError, TimeoutError) as e:
                print(f"Error collecting frame from {camera.camera_id}: {e}")
        
        return frames
