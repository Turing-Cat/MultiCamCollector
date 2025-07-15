import pyrealsense2 as rs
import numpy as np
import time
from typing import Iterator, Tuple

from src.services.abstract_camera import AbstractCamera
from src.models.camera import Frame
from src.services.storage_service import StorageService

class RealsenseCamera(AbstractCamera):
    """
    Concrete implementation of AbstractCamera for Intel RealSense cameras.
    This class handles the connection, frame capture, and data conversion
    for RealSense devices, outputting depth data in meters.
    """

    def __init__(self, camera_id: str, serial_number: str, resolution_wh: Tuple[int, int], fps: int, storage_service: StorageService):
        self._camera_id = camera_id
        self._serial_number = serial_number
        self._width, self._height = resolution_wh
        self._fps = fps
        self._storage_service = storage_service
        
        self._pipeline = None
        self._config = None
        self._align = None
        self._is_connected = False
        self._sequence_id = 0
        self._depth_scale = None

        # Load configuration once during initialization to avoid repeated file access
        from src.services.config_service import ConfigService
        config = ConfigService()
        self._frame_timeout_ms = config.frame_timeout_ms
        self._post_processing_enabled = config.get('post_processing.enabled', False)
        
        if self._post_processing_enabled:
            self._depth_to_disparity = rs.disparity_transform(True)
            self._spatial_filter = rs.spatial_filter()
            self._spatial_filter.set_option(rs.option.filter_smooth_alpha, 0.5)
            self._spatial_filter.set_option(rs.option.filter_smooth_delta, 25)
            self._spatial_filter.set_option(rs.option.filter_magnitude, 2)
            self._spatial_filter.set_option(rs.option.holes_fill, 0)
            
            self._temporal_filter = rs.temporal_filter()
            self._temporal_filter.set_option(rs.option.filter_smooth_alpha, 0.1)
            self._temporal_filter.set_option(rs.option.filter_smooth_delta, 20)
            self._temporal_filter.set_option(rs.option.holes_fill, 0)
            
            self._disparity_to_depth = rs.disparity_transform(False)
            self._hole_filling_filter = rs.hole_filling_filter()
            self._hole_filling_filter.set_option(rs.option.holes_fill, 2)

    def _apply_post_processing(self, depth_frame: rs.depth_frame) -> rs.depth_frame:
        """Applies a chain of post-processing filters to the depth frame."""
        frame = self._depth_to_disparity.process(depth_frame)
        frame = self._spatial_filter.process(frame)
        frame = self._temporal_filter.process(frame)
        frame = self._disparity_to_depth.process(frame)
        frame = self._hole_filling_filter.process(frame)
        return frame

    def connect(self) -> None:
        """Initializes and connects to the camera, and stores the depth scale."""
        try:
            print(f"Attempting to connect RealSense camera {self._camera_id} with {self._width}x{self._height} @ {self._fps}fps...")
            
            ctx = rs.context()
            self._pipeline = rs.pipeline(ctx)
            self._config = rs.config()
            
            self._config.enable_device(self._serial_number)
            self._config.enable_stream(rs.stream.color, self._width, self._height, rs.format.bgr8, self._fps)
            self._config.enable_stream(rs.stream.depth, self._width, self._height, rs.format.z16, self._fps)
            
            profile = self._pipeline.start(self._config)
            
            depth_sensor = profile.get_device().first_depth_sensor()
            self._depth_scale = depth_sensor.get_depth_scale()
            
            self._save_intrinsics(profile)
            self._align = rs.align(rs.stream.color)
            
            self._is_connected = True
            print(f"RealSense camera {self._camera_id} connected successfully. Depth scale: {self._depth_scale}")

        except rs.error as e:
            print(f"Error: Failed to connect RealSense camera {self._camera_id}: {e}")
            self._is_connected = False
            raise

    def _save_intrinsics(self, profile):
        """Saves the camera intrinsics, including depth scale, to a file."""
        import json
        import os
        
        root_dir = self._storage_service.get_root_dir()
        intrinsics_dir = os.path.join(root_dir, "intrinsics")
        os.makedirs(intrinsics_dir, exist_ok=True)
        
        intrinsics_path = os.path.join(intrinsics_dir, f"intrinsics_{self._serial_number}.json")

        streams = profile.get_streams()
        intrinsics_data = {}

        for stream in streams:
            if stream.is_video_stream_profile():
                vsp = stream.as_video_stream_profile()
                intrinsics = vsp.get_intrinsics()
                
                stream_data = {
                    "width": intrinsics.width,
                    "height": intrinsics.height,
                    "ppx": intrinsics.ppx,
                    "ppy": intrinsics.ppy,
                    "fx": intrinsics.fx,
                    "fy": intrinsics.fy,
                    "model": str(intrinsics.model),
                    "coeffs": intrinsics.coeffs,
                }
                
                if vsp.stream_type() == rs.stream.depth:
                    stream_data["depth_scale"] = self._depth_scale
                
                intrinsics_data[vsp.stream_name()] = stream_data

        with open(intrinsics_path, "w") as f:
            json.dump(intrinsics_data, f, indent=4)
        print(f"Saved intrinsics for {self._camera_id} to {intrinsics_path}")

    def disconnect(self) -> None:
        if self._is_connected and self._pipeline:
            self._pipeline.stop()
        self._is_connected = False
        print(f"RealSense camera {self._camera_id} disconnected.")

    def capture_frame(self) -> Frame:
        # Enhanced pre-capture check for robustness
        if not self.is_connected or not self._pipeline or not self._align or self._depth_scale is None:
            return None
        
        try:
            # Use pre-configured timeout
            frameset = self._pipeline.wait_for_frames(timeout_ms=self._frame_timeout_ms)
        except rs.error as e:
            # Specific RealSense error (e.g., device disconnected)
            print(f"[{self._camera_id}] RealSense SDK error in wait_for_frames(): {e}")
            self.disconnect()
            return None
        except RuntimeError as e:
            # This is often a timeout, which is expected, so we don't spam the log.
            error_msg = str(e).lower()
            if "timeout" not in error_msg and "didn't arrive within" not in error_msg:
                print(f"[{self._camera_id}] Runtime error in wait_for_frames(): {e}")
            return None
        
        try:
            if not frameset:
                return None

            aligned_frames = self._align.process(frameset)
            color_frame = aligned_frames.get_color_frame()
            depth_frame = aligned_frames.get_depth_frame()

            if not color_frame or not depth_frame:
                return None

            if self._post_processing_enabled:
                depth_frame = self._apply_post_processing(depth_frame)

            rgb_image = np.asanyarray(color_frame.get_data())[:, :, ::-1].copy()
            
            depth_data = np.asanyarray(depth_frame.get_data())
            # Convert raw depth (uint16) to meters (float32)
            depth_image = depth_data.astype(np.float32) * self._depth_scale

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
        except rs.error as e:
            print(f"[{self._camera_id}] RealSense SDK error during frame processing: {e}")
            return None
        except Exception as e:
            print(f"[{self._camera_id}] Unexpected error during frame processing: {e}")
            return None

    def stream(self) -> Iterator[Frame]:
        while self._is_connected:
            frame = self.capture_frame()
            if frame:
                yield frame

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    @property
    def camera_id(self) -> str:
        return self._camera_id

    @property
    def fps(self) -> int:
        return self._fps
