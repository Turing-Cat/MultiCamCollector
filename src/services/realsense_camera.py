from src.services import sdk_loader
import pyrealsense2 as rs
import numpy as np
import time
from typing import Iterator, Tuple

from src.services.abstract_camera import AbstractCamera
from src.models.camera import Frame

class RealsenseCamera(AbstractCamera):
    """Concrete implementation of AbstractCamera for Intel RealSense cameras."""

    def __init__(self, camera_id: str, serial_number: str, width: int, height: int, fps: int):
        self._camera_id = camera_id
        self._serial_number = serial_number
        self._width = width
        self._height = height
        self._fps = fps
        
        self._pipeline = rs.pipeline()
        self._config = rs.config()
        self._align = rs.align(rs.stream.color)
        self._is_connected = False
        self._sequence_id = 0


    

    def connect(self) -> None:
        try:
            print(f"Attempting to connect RealSense camera {self._camera_id} with {self._width}x{self._height} @ {self._fps}fps...")
            self._config.enable_device(self._serial_number)
            self._config.enable_stream(rs.stream.color, self._width, self._height, rs.format.bgr8, self._fps)
            self._config.enable_stream(rs.stream.depth, self._width, self._height, rs.format.z16, self._fps)
            profile = self._pipeline.start(self._config)
            
            self._align = rs.align(rs.stream.color)
            
            self._is_connected = True
            print(f"RealSense camera {self._camera_id} connected successfully.")

        except Exception as e:
            print(f"Warning: Failed to connect RealSense camera {self._camera_id} with primary config: {e}")
            print("Attempting fallback configuration (640x480 @ 30fps)...")
            
            # Clean up previous config attempt
            self._pipeline = rs.pipeline()
            self._config = rs.config()
            
            try:
                self._config.enable_device(self._serial_number)
                self._config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
                self._config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
                profile = self._pipeline.start(self._config)

                self._align = rs.align(rs.stream.color)
                
                self._is_connected = True
                print(f"RealSense camera {self._camera_id} connected with fallback configuration.")

                # Pre-heat to allow auto-exposure to settle
                for _ in range(30):
                    self._pipeline.poll_for_frames()
                    time.sleep(0.03)
            except Exception as fallback_e:
                print(f"Error: Failed to connect to RealSense camera {self._camera_id} with fallback config: {fallback_e}")
                self._is_connected = False

    def disconnect(self) -> None:
        if self._is_connected:
            self._pipeline.stop()
            self._is_connected = False
            print(f"RealSense camera {self._camera_id} disconnected.")

    def capture_frame(self) -> Frame:
        if not self._is_connected:
            raise ConnectionError(f"Camera {self._camera_id} is not connected.")
        
        frames = self._pipeline.wait_for_frames(timeout_ms=10000)
        aligned_frames = self._align.process(frames)
        color_frame = aligned_frames.get_color_frame()
        depth_frame = aligned_frames.get_depth_frame()

        if not color_frame or not depth_frame:
            raise RuntimeError("Failed to get RealSense frames.")

        rgb_image = np.asanyarray(color_frame.get_data()).copy()
        depth_image = np.asanyarray(depth_frame.get_data()).copy()

        timestamp_ns = int(time.time_ns())
        frame = Frame(
            camera_id=self._camera_id,
            sequence_id=self._sequence_id,
            timestamp_ns=timestamp_ns,
            rgb_image=rgb_image,
            depth_image=depth_image,
            rgb_image_right=None
        )
        self._sequence_id += 1
        return frame

    def stream(self) -> Iterator[Frame]:
        while self._is_connected:
            yield self.capture_frame()

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    @property
    def camera_id(self) -> str:
        return self._camera_id
