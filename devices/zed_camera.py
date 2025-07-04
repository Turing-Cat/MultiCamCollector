import pyzed.sl as sl
import numpy as np
import time
from typing import Iterator

from devices.abstract_camera import AbstractCamera
from models.camera import Frame

class ZedCamera(AbstractCamera):
    """Concrete implementation of AbstractCamera for ZED cameras."""

    def __init__(self, camera_id: str, serial_number: str):
        self._camera_id = camera_id
        self._serial_number = serial_number
        self._zed = sl.Camera()
        self._init_params = sl.InitParameters()
        self._is_connected = False
        self._sequence_id = 0

        self._init_params.camera_resolution = sl.RESOLUTION.HD720
        self._init_params.camera_fps = 30
        self._init_params.depth_mode = sl.DEPTH_MODE.PERFORMANCE
        self._init_params.coordinate_units = sl.UNIT.MILLIMETER
        self._init_params.depth_stabilization = True
        self._init_params.depth_minimum_distance = 200
        self._init_params.set_from_serial_number(int(self._serial_number))

    def connect(self) -> None:
        status = self._zed.open(self._init_params)
        if status != sl.ERROR_CODE.SUCCESS:
            print(f"Error connecting to ZED camera {self._camera_id}: {status}")
            self._is_connected = False
            raise ConnectionError(f"ZED Camera connection error: {status}")
        else:
            self._is_connected = True
            print(f"ZED camera {self._camera_id} connected.")

    def disconnect(self) -> None:
        if self._is_connected:
            self._zed.close()
            self._is_connected = False
            print(f"ZED camera {self._camera_id} disconnected.")

    def capture_frame(self) -> Frame:
        if not self._is_connected:
            raise ConnectionError(f"Camera {self._camera_id} is not connected.")

        runtime_params = sl.RuntimeParameters()
        if self._zed.grab(runtime_params) == sl.ERROR_CODE.SUCCESS:
            image_sl = sl.Mat()
            depth_sl = sl.Mat()
            self._zed.retrieve_image(image_sl, sl.VIEW.LEFT)
            self._zed.retrieve_measure(depth_sl, sl.MEASURE.DEPTH)

            rgb_image = image_sl.get_data()[:, :, :3]
            depth_image = depth_sl.get_data()

            timestamp_ns = int(time.time_ns())
            frame = Frame(
                camera_id=self._camera_id,
                sequence_id=self._sequence_id,
                timestamp_ns=timestamp_ns,
                rgb_image=rgb_image,
                depth_image=depth_image
            )
            self._sequence_id += 1
            return frame
        else:
            raise RuntimeError("Failed to grab ZED frame.")

    def stream(self) -> Iterator[Frame]:
        while self._is_connected:
            yield self.capture_frame()

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    @property
    def camera_id(self) -> str:
        return self._camera_id

