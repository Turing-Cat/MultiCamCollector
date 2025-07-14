from typing import Dict, Any, Tuple

from src.services.abstract_camera import AbstractCamera
from src.services.realsense_camera import RealsenseCamera
from src.services.mock_camera import MockCamera


class CameraFactory:
    """A factory to create camera instances."""

    @staticmethod
    def create_camera(
        camera_id: str,
        camera_type: str,
        device_info: Dict[str, Any],
        camera_config: Dict[str, Any]
    ) -> AbstractCamera:
        """
        Creates a camera instance based on the camera type.

        Args:
            camera_id: The unique ID of the camera.
            camera_type: The type of camera ('realsense' or 'zed').
            device_info: Information about the specific device (e.g., serial number).
            camera_config: Configuration settings for the camera.

        Returns:
            An instance of a class that inherits from AbstractCamera.
        """
        if camera_type == 'mock':
            return MockCamera(
                camera_id=camera_id,
                model=device_info.get('model', 'Mock'),
                config=camera_config
            )

        resolution = (camera_config['width'], camera_config['height'])
        fps = camera_config['fps']

        if camera_type == 'realsense':
            return RealsenseCamera(
                camera_id=camera_id,
                serial_number=device_info['serial_number'],
                resolution_wh=resolution,
                fps=fps
            )
        else:
            raise ValueError(f"Unknown camera type: {camera_type}")

