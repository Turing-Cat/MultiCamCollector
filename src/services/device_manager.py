import pyrealsense2 as rs
import pyzed.sl as sl
from typing import List, Dict, Any
import platform
import os
from src.services.config_service import ConfigService
from src.services.camera_factory import CameraFactory

class DeviceManager:
    """Manages the discovery and status of connected cameras."""

    def __init__(self, zed_sdk_path=None):
        self._camera_configs: List[Dict[str, Any]] = []
        self._config_service = ConfigService()
        self.factory = CameraFactory()
        if zed_sdk_path:
            self._set_zed_sdk_path(zed_sdk_path)

    def _set_zed_sdk_path(self, zed_sdk_path):
        """Set the ZED SDK path for the current OS."""
        if platform.system() == "Windows":
            os.add_dll_directory(zed_sdk_path)
        elif platform.system() == "Linux":
            pass

    def discover_cameras(self) -> None:
        """Discover all available cameras and store their configurations."""
        self._camera_configs = []
        self._discover_realsense_cameras()
        self._discover_zed_cameras()

        if not self._camera_configs:
            print("No real cameras found. Falling back to mock cameras.")
            self._create_mock_camera_configs()

    def _discover_realsense_cameras(self):
        """Discover and store configurations for RealSense cameras."""
        try:
            ctx = rs.context()
            devices = ctx.query_devices()
            for dev in devices:
                serial_number = dev.get_info(rs.camera_info.serial_number)
                camera_id = f"RealSense_{serial_number}"
                width, height = self._config_service.camera_resolution
                camera_config = {
                    "width": width,
                    "height": height,
                    "fps": self._config_service.camera_fps
                }
                
                self._camera_configs.append({
                    "camera_id": camera_id,
                    "type": "realsense",
                    "device_info": {"serial_number": serial_number},
                    "config": camera_config
                })
                print(f"Found RealSense camera: {camera_id}")
        except Exception as e:
            print(f"Error discovering RealSense cameras: {e}")

    def _discover_zed_cameras(self):
        """Discover and store configurations for ZED cameras."""
        try:
            zed_list = sl.Camera.get_device_list()
            for zed_info in zed_list:
                serial_number = str(zed_info.serial_number)
                camera_id = f"ZED_{serial_number}"
                width, height = self._config_service.camera_resolution
                camera_config = {
                    "width": width,
                    "height": height,
                    "fps": self._config_service.camera_fps
                }
                camera_config.update(self._config_service.zed_settings)

                self._camera_configs.append({
                    "camera_id": camera_id,
                    "type": "zed",
                    "device_info": {"serial_number": serial_number},
                    "config": camera_config
                })
                print(f"Found ZED camera: {camera_id}")
        except Exception as e:
            print(f"Error discovering ZED cameras: {e}")

    def _create_mock_camera_configs(self):
        """Create mock camera configurations for development."""
        print("Creating mock camera configuration.")
        width, height = self._config_service.camera_resolution
        mock_config = {
            "camera_id": "Mock_1",
            "type": "mock",
            "device_info": {"serial_number": "MOCK_SN_1"},
            "config": {
                "resolution": (width, height),
                "fps": self._config_service.camera_fps
            }
        }
        self._camera_configs.append(mock_config)

    def get_all_camera_configs(self) -> List[Dict[str, Any]]:
        """Get a list of all discovered camera configurations."""
        return self._camera_configs

