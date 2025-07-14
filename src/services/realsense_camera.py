from src.services import sdk_loader
import pyrealsense2 as rs
import numpy as np
import time
from typing import Iterator, Tuple

from src.services.abstract_camera import AbstractCamera
from src.models.camera import Frame
import cv2

class RealsenseCamera(AbstractCamera):
    """Concrete implementation of AbstractCamera for Intel RealSense cameras."""

    def __init__(self, camera_id: str, serial_number: str, resolution_wh: Tuple[int, int], fps: int):
        self._camera_id = camera_id
        self._serial_number = serial_number
        self._width, self._height = resolution_wh
        self._fps = fps
        
        # Initialize SDK objects to None. They will be created in the worker thread.
        self._pipeline = None
        self._config = None
        self._align = None
        self._is_connected = False
        self._sequence_id = 0

    def connect(self) -> None:
        """Initializes and connects to the camera. Must be called from the target worker thread."""
        try:
            print(f"Attempting to connect RealSense camera {self._camera_id} with {self._width}x{self._height} @ {self._fps}fps...")
            
            # Create a dedicated context for each camera to ensure thread safety.
            ctx = rs.context()
            self._pipeline = rs.pipeline(ctx)
            self._config = rs.config()
            
            # It's crucial to enable the device on the config for this context.
            self._config.enable_device(self._serial_number)
            self._config.enable_stream(rs.stream.color, self._width, self._height, rs.format.bgr8, self._fps)
            self._config.enable_stream(rs.stream.depth, self._width, self._height, rs.format.z16, self._fps)
            
            profile = self._pipeline.start(self._config)
            self._align = rs.align(rs.stream.color)
            
            self._is_connected = True
            print(f"RealSense camera {self._camera_id} connected successfully.")

        except RuntimeError as e:
            print(f"Warning: Failed to connect RealSense camera {self._camera_id} with primary config: {e}")
            # Fallback logic can be added here if necessary, ensuring objects are re-initialized.
            self._is_connected = False
            raise  # Re-raise the exception to be caught by the worker

    def disconnect(self) -> None:
        if self._is_connected and self._pipeline:
            self._pipeline.stop()
        self._is_connected = False
        print(f"RealSense camera {self._camera_id} disconnected.")

    def capture_frame(self) -> Frame:
        if not self.is_connected or not self._pipeline:
            return None
        
        # Load timeout from config
        from src.services.config_service import ConfigService
        config = ConfigService()
        timeout_ms = config.frame_timeout_ms
        
        try:
            # Use configurable timeout for better responsiveness
            frameset = self._pipeline.wait_for_frames(timeout_ms=timeout_ms)
        except RuntimeError as e:
            # RealSense SDK throws RuntimeError for timeouts and other issues
            # Don't print every timeout to reduce log spam
            error_msg = str(e).lower()
            if "timeout" not in error_msg and "didn't arrive within" not in error_msg:
                print(f"[{self._camera_id}] wait_for_frames() failed: {e}")
            return None
        except Exception as e:
            print(f"[{self._camera_id}] Unexpected error in wait_for_frames(): {e}")
            return None
        
        try:
            if not frameset:
                return None

            aligned_frames = self._align.process(frameset)
            color_frame = aligned_frames.get_color_frame()
            depth_frame = aligned_frames.get_depth_frame()

            if not color_frame or not depth_frame:
                return None

            # Safely extract RGB image
            rgb_image = None
            try:
                bgr_img = np.asanyarray(color_frame.get_data())
                if bgr_img is not None and bgr_img.size > 0 and len(bgr_img.shape) == 3:
                    rgb_image = bgr_img[:, :, ::-1].copy()       # BGR ➜ RGB
            except Exception as e:
                print(f"Error converting RGB image for {self._camera_id}: {e}")
                rgb_image = None
            
            # Safely extract depth image
            depth_image = None
            try:
                depth_data = np.asanyarray(depth_frame.get_data())
                if depth_data is not None and depth_data.size > 0:
                    depth_image = depth_data.copy() # 固定深度范围
            except Exception as e:
                print(f"Error converting depth image for {self._camera_id}: {e}")
                depth_image = None

            # Only return frame if we have valid RGB data
            if rgb_image is None:
                return None

            timestamp_ns = int(time.time_ns())
            frame = Frame(
                camera_id=self._camera_id,
                frame_number=self._sequence_id,
                timestamp_ns=timestamp_ns,
                rgb_image=rgb_image,
                depth_image=depth_image
            )
            self._sequence_id += 1
            return frame
        except Exception as e:
            print(f"Error in RealsenseCamera.capture_frame(): {e}")
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
