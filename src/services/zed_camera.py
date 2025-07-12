import pyzed.sl as sl
import numpy as np
import time
from typing import Iterator, Dict, Any, Tuple
import cv2

from src.services.abstract_camera import AbstractCamera
from src.models.camera import Frame

class ZedCamera(AbstractCamera):
    """ZED camera implementation, supporting color and depth frame capture."""

    RESOLUTION_MAP = {
        "2208x1242": sl.RESOLUTION.HD2K,
        "1920x1080": sl.RESOLUTION.HD1080,
        "1280x720": sl.RESOLUTION.HD720,
        "672x376": sl.RESOLUTION.VGA,
    }

    def __init__(self, camera_id: str, serial_number: str, resolution_wh: Tuple[int, int], fps: int, zed_config: Dict[str, Any]):
        self._camera_id = camera_id
        self._serial_number = serial_number
        self._resolution_wh = resolution_wh
        self._fps = fps
        self._zed_config = zed_config

        # Initialize SDK objects to None. They will be created in the worker thread.
        self._zed = None
        self._init_params = None
        self._image_sl = None
        self._image_right_sl = None
        self._depth_sl = None
        self._is_connected = False
        self._sequence_id = 0

    def _apply_config(self):
        """Applies settings from the provided configuration."""
        res_str = f"{self._resolution_wh[0]}x{self._resolution_wh[1]}"
        self._init_params.camera_resolution = self.RESOLUTION_MAP.get(res_str, sl.RESOLUTION.HD720)
        self._init_params.camera_fps = self._fps
        self._init_params.depth_mode = getattr(sl.DEPTH_MODE, self._zed_config.get("depth_mode", "PERFORMANCE"))
        self._init_params.depth_stabilization = int(bool(self._zed_config.get("depth_stabilization", True)))
        self._init_params.camera_disable_self_calib = not bool(self._zed_config.get("enable_self_calibration", False))
        self._init_params.depth_minimum_distance = int(self._zed_config.get("depth_minimum_distance", 200))
        self._init_params.set_from_serial_number(int(self._serial_number))
        print(f"ZED config loaded: {res_str} @ {self._init_params.camera_fps}fps, Depth: {self._init_params.depth_mode}")

    def connect(self) -> None:
        """Initializes and connects to the ZED camera. Must be called from the target worker thread."""
        print(f"Connecting to ZED camera {self._camera_id}...")
        
        # Create SDK objects on this thread
        self._zed = sl.Camera()
        self._init_params = sl.InitParameters()
        self._apply_config()

        status = self._zed.open(self._init_params)
        if status != sl.ERROR_CODE.SUCCESS:
            raise ConnectionError(f"ZED Camera connection error: {status}")

        # Create persistent sl.Mat objects after successful connection
        cam_info = self._zed.get_camera_information()
        width = cam_info.camera_configuration.resolution.width
        height = cam_info.camera_configuration.resolution.height
        self._image_sl = sl.Mat(width, height, sl.MAT_TYPE.U8_C4)
        self._image_right_sl = sl.Mat(width, height, sl.MAT_TYPE.U8_C4)
        self._depth_sl = sl.Mat(width, height, sl.MAT_TYPE.F32_C1)
        
        self._is_connected = True
        print(f"ZED camera {self._camera_id} connected successfully.")

    def disconnect(self) -> None:
        if self._is_connected and self._zed:
            self._zed.close()
        self._is_connected = False
        print(f"ZED camera {self._camera_id} disconnected.")

    def capture_frame(self) -> Frame:
        if not self.is_connected or not self._zed:
            return None

        runtime_params = sl.RuntimeParameters()
        try:
            if self._zed.grab(runtime_params) == sl.ERROR_CODE.SUCCESS:
                # A new image is available
                rgb_image = None
                rgb_image_right = None
                depth_image = None
                
                # Retrieve left image
                try:
                    if self._zed.retrieve_image(self._image_sl, sl.VIEW.LEFT) == sl.ERROR_CODE.SUCCESS:
                        data_left = self._image_sl.get_data()
                        if data_left is not None and data_left.size > 0:
                            bgr_left = data_left[:, :, :3]
                            rgb_image = cv2.cvtColor(bgr_left, cv2.COLOR_BGR2RGB)
                except Exception as e:
                    print(f"Error retrieving left image: {e}")
                    rgb_image = None

                # Retrieve right image
                try:
                    if self._zed.retrieve_image(self._image_right_sl, sl.VIEW.RIGHT) == sl.ERROR_CODE.SUCCESS:
                        data_right = self._image_right_sl.get_data()
                        if data_right is not None and data_right.size > 0:
                            bgr_right = data_right[:, :, :3]
                            rgb_image_right = cv2.cvtColor(bgr_right, cv2.COLOR_BGR2RGB)
                except Exception as e:
                    print(f"Error retrieving right image: {e}")
                    rgb_image_right = None

                # Retrieve depth image
                try:
                    if self._zed.retrieve_measure(self._depth_sl, sl.MEASURE.DEPTH) == sl.ERROR_CODE.SUCCESS:
                        depth_data = self._depth_sl.get_data()
                        if depth_data is not None and depth_data.size > 0:
                            depth_image = depth_data.copy()
                except Exception as e:
                    print(f"Error retrieving depth image: {e}")
                    depth_image = None

                frame = Frame(
                    camera_id=self._camera_id,
                    frame_number=self._sequence_id,
                    timestamp_ns=time.time_ns(),
                    rgb_image=rgb_image,
                    rgb_image_left=rgb_image,
                    rgb_image_right=rgb_image_right,
                    depth_image=depth_image
                )
                self._sequence_id += 1
                return frame
            return None
        except Exception as e:
            print(f"Error in ZedCamera.capture_frame(): {e}")
            return None

    def stream(self) -> Iterator[Frame]:
        while self._is_connected:
            yield self.capture_frame()

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    @property

    def camera_id(self) -> str:
        return self._camera_id

    @property
    def fps(self) -> int:
        return self._fps
