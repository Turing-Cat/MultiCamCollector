import pyrealsense2 as rs
import pyzed.sl as sl
import time
import threading
from typing import List
from devices.abstract_camera import AbstractCamera
from devices.realsense_camera import RealsenseCamera
from devices.zed_camera import ZedCamera
from devices.mock_camera import MockCamera

class DeviceManager:
    """Manages the discovery and status of connected cameras."""

    def __init__(self):
        self._cameras: List[AbstractCamera] = []
        self._monitoring_thread = None
        self._stop_event = threading.Event()

    def discover_cameras(self) -> None:
        """Discover and connect to all available cameras."""
        self._cameras = []
        self._discover_realsense_cameras()
        self._discover_zed_cameras()

        if not self._cameras:
            print("No real cameras found. Falling back to mock cameras.")
            self._create_mock_cameras()

        for camera in self._cameras:
            try:
                camera.connect()
            except Exception as e:
                print(f"Could not connect to camera {camera.camera_id}: {e}")

    def _discover_realsense_cameras(self):
        """Discover and initialize RealSense cameras."""
        try:
            ctx = rs.context()
            devices = ctx.query_devices()
            for i, dev in enumerate(devices):
                serial_number = dev.get_info(rs.camera_info.serial_number)
                camera_id = f"RealSense_{serial_number}"
                camera = RealsenseCamera(camera_id=camera_id, serial_number=serial_number)
                self._cameras.append(camera)
                print(f"Found RealSense camera: {camera_id}")
        except Exception as e:
            print(f"Error discovering RealSense cameras: {e}")

    def _discover_zed_cameras(self):
        """Discover and initialize ZED cameras."""
        try:
            zed_list = sl.Camera.get_device_list()
            for i, zed_info in enumerate(zed_list):
                serial_number = str(zed_info.serial_number)
                camera_id = f"ZED_{serial_number}"
                camera = ZedCamera(camera_id=camera_id, serial_number=serial_number)
                self._cameras.append(camera)
                print(f"Found ZED camera: {camera_id}")
        except Exception as e:
            print(f"Error discovering ZED cameras: {e}")

    def _create_mock_cameras(self):
        """Create mock cameras for development when no real cameras are found."""
        self._cameras = [
            MockCamera(camera_id="D435i_1", model="D435i"),
            MockCamera(camera_id="D435i_2", model="D435i"),
            MockCamera(camera_id="D435i_3", model="D435i"),
            MockCamera(camera_id="D435i_4", model="D435i"),
            MockCamera(camera_id="ZED2i_1", model="ZED2i")
        ]

    def start_monitoring(self):
        """Start the camera connection monitoring thread."""
        if self._monitoring_thread is None:
            self._stop_event.clear()
            self._monitoring_thread = threading.Thread(target=self._monitor_cameras, daemon=True)
            self._monitoring_thread.start()
            print("Camera monitoring started.")

    def stop_monitoring(self):
        """Stop the camera connection monitoring thread."""
        if self._monitoring_thread is not None:
            self._stop_event.set()
            self._monitoring_thread.join()
            self._monitoring_thread = None
            print("Camera monitoring stopped.")

    def _monitor_cameras(self):
        """Periodically check camera connections and attempt to reconnect."""
        while not self._stop_event.is_set():
            for camera in self._cameras:
                if not camera.check_connection():
                    print(f"Camera {camera.camera_id} disconnected. Attempting to reconnect...")
                    try:
                        camera.disconnect()  # Ensure clean state
                        camera.connect()
                        if camera.is_connected:
                            print(f"Camera {camera.camera_id} reconnected successfully.")
                    except Exception as e:
                        print(f"Failed to reconnect to {camera.camera_id}: {e}")
            time.sleep(5)  # Check every 5 seconds

    def get_all_cameras(self) -> List[AbstractCamera]:
        """Get a list of all discovered cameras."""
        return self._cameras

    def get_camera_by_id(self, camera_id: str) -> AbstractCamera:
        """Get a camera by its ID."""
        for camera in self._cameras:
            if camera.camera_id == camera_id:
                return camera
        raise ValueError(f"Camera with ID {camera_id} not found.")
