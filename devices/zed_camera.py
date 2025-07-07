import pyzed.sl as sl
import numpy as np
import time
import yaml
from typing import Iterator

from devices.abstract_camera import AbstractCamera
from models.camera import Frame


class ZedCamera(AbstractCamera):
    """ZED 摄像头实现，支持彩色 + 深度帧采集。"""

    # Map resolution strings from config to ZED SDK enums
    RESOLUTION_MAP = {
        "2208x1242": sl.RESOLUTION.HD2K,
        "1920x1080": sl.RESOLUTION.HD1080,
        "1280x720": sl.RESOLUTION.HD720,
        "672x376": sl.RESOLUTION.VGA,
    }

    def __init__(self, camera_id: str, serial_number: str):
        # 基本属性
        self._camera_id = camera_id
        self._serial_number = serial_number
        self._zed = sl.Camera()
        self._init_params = sl.InitParameters()
        self._is_connected = False
        self._sequence_id = 0

        # 从配置文件加载并设置参数
        self._apply_config()
        
        self._init_params.set_from_serial_number(int(self._serial_number))

        # -------- 关键改动：持久化 Mat --------
        self._image_sl: sl.Mat = sl.Mat()
        self._depth_sl: sl.Mat = sl.Mat()
        # ------------------------------------

    def _apply_config(self):
        """Loads settings from config.yaml and applies them to ZED init parameters."""
        try:
            with open("config.yaml", "r") as f:
                config = yaml.safe_load(f)
                
                # Resolution and FPS
                res_str = config.get("camera_resolution", "1280x720")
                self._init_params.camera_resolution = self.RESOLUTION_MAP.get(res_str, sl.RESOLUTION.HD720)
                self._init_params.camera_fps = int(config.get("camera_fps", 30))
                
                # ZED-specific settings
                zed_config = config.get("zed", {})
                self._init_params.depth_mode = getattr(sl.DEPTH_MODE, zed_config.get("depth_mode", "PERFORMANCE"))
                self._init_params.depth_stabilization = bool(zed_config.get("depth_stabilization", True))
                self._init_params.depth_minimum_distance = int(zed_config.get("depth_minimum_distance", 200))
                self._init_params.camera_disable_self_calib = not bool(zed_config.get("enable_self_calibration", False))

                print(f"ZED config loaded: {res_str} @ {self._init_params.camera_fps}fps, Depth: {self._init_params.depth_mode}")

        except (FileNotFoundError, KeyError, ValueError, AttributeError) as e:
            print(f"Warning: Could not load or parse config.yaml ({e}). Using default ZED settings.")
            # Apply default settings
            self._init_params.camera_resolution = sl.RESOLUTION.HD720
            self._init_params.camera_fps = 30
            self._init_params.depth_mode = sl.DEPTH_MODE.PERFORMANCE
            self._init_params.coordinate_units = sl.UNIT.MILLIMETER
            self._init_params.depth_stabilization = True
            self._init_params.depth_minimum_distance = 200
            self._init_params.camera_disable_self_calib = True

    # --------------------------------------------------------------------- #
    # 连接 / 断开
    # --------------------------------------------------------------------- #

    def connect(self) -> None:
        """连接 ZED 相机，并处理常见错误。"""
        print(f"Connecting to ZED camera {self._camera_id}...")

        status = self._zed.open(self._init_params)

        if status == sl.ERROR_CODE.SUCCESS:
            self._is_connected = True
            print(f"ZED camera {self._camera_id} connected successfully.")

        elif status == sl.ERROR_CODE.CAMERA_NOT_DETECTED:
            raise ConnectionError(
                f"ZED Camera {self._camera_id} not detected. Check USB connection."
            )
        elif status == sl.ERROR_CODE.CAMERA_DETECTION_ISSUE:
            raise ConnectionError(
                f"ZED Camera {self._camera_id} detection issue. Try reconnecting the camera."
            )
        elif status == sl.ERROR_CODE.INVALID_FUNCTION_PARAMETERS:
            raise ConnectionError(
                f"ZED Camera {self._camera_id} invalid parameters. Check serial number."
            )
        else:
            raise ConnectionError(f"ZED Camera connection error: {status}")

    def disconnect(self) -> None:
        """关闭相机并释放内存。"""
        if not self._is_connected:
            return

        # 释放持久 Mat 所占 CPU 内存
        if self._image_sl.is_init():   # is_init() 由 ZED SDK 提供
            self._image_sl.free()
        if self._depth_sl.is_init():
            self._depth_sl.free()

        self._zed.close()
        self._is_connected = False
        print(f"ZED camera {self._camera_id} disconnected.")

    # --------------------------------------------------------------------- #
    # 采集帧
    # --------------------------------------------------------------------- #

    def capture_frame(self) -> Frame:
        """抓取一帧彩色+深度，并拷贝到安全的 NumPy 数组。"""
        if not self._is_connected:
            raise ConnectionError(f"Camera {self._camera_id} is not connected.")

        runtime_params = sl.RuntimeParameters()

        if self._zed.grab(runtime_params) != sl.ERROR_CODE.SUCCESS:
            raise RuntimeError("Failed to grab ZED frame.")

        # 复用持久 Mat，避免每帧重新分配
        self._zed.retrieve_image(self._image_sl, sl.VIEW.LEFT)
        self._zed.retrieve_measure(self._depth_sl, sl.MEASURE.DEPTH)

        # 关键：立即 copy，解除对 Mat 生命周期的依赖
        rgb_image = self._image_sl.get_data().copy()[:, :, :3]
        depth_image = self._depth_sl.get_data().copy()

        frame = Frame(
            camera_id=self._camera_id,
            sequence_id=self._sequence_id,
            timestamp_ns=time.time_ns(),
            rgb_image=rgb_image,
            depth_image=depth_image,
        )

        self._sequence_id += 1
        return frame

    def stream(self) -> Iterator[Frame]:
        """持续产出帧，可与 for/while 组合使用。"""
        while self._is_connected:
            yield self.capture_frame()

    # --------------------------------------------------------------------- #
    # 属性
    # --------------------------------------------------------------------- #

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    @property
    def camera_id(self) -> str:
        return self._camera_id
