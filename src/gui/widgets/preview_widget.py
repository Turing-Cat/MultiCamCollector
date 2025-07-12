import os
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QLabel, QGridLayout, QFrame, QHBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt6.QtGui import QImage, QPixmap
import cv2
import numpy as np
import time
import threading
from src.services.abstract_camera import AbstractCamera
from src.services.config_service import ConfigService

from src.services.camera_factory import CameraFactory


class FrameWorker(QObject):
    """Worker to connect to a camera and fetch frames in a background thread."""
    frame_ready = pyqtSignal(object)
    connection_status = pyqtSignal(str, bool, str)  # camera_id, is_connected, message

    def __init__(self, camera_config: dict, factory: CameraFactory):
        super().__init__()
        self.camera_config = camera_config
        self.factory = factory
        self.camera = None  # Will be created in the run method
        self.running = True
        self._lock = threading.Lock()
        self._last_frame = None
        self._last_emit_time = 0
        
        # Load UI performance settings from config
        from src.services.config_service import ConfigService
        config = ConfigService()
        self._ui_fps_limit = config.display_fps
        self._ui_frame_interval = 1.0 / self._ui_fps_limit

    def run(self):
        """Create and connect to the camera, then continuously fetch frames."""
        try:
            # Create the camera instance inside the thread
            self.camera = self.factory.create_camera(
                camera_id=self.camera_config['camera_id'],
                camera_type=self.camera_config['type'],
                device_info=self.camera_config['device_info'],
                camera_config=self.camera_config['config']
            )
            
            print(f"Attempting to connect to {self.camera.camera_id} in worker thread...")
            self.camera.connect()
            self.connection_status.emit(self.camera.camera_id, True, "Connected")
            print(f"{self.camera.camera_id} connected successfully in worker thread.")

            while self.running:
                try:
                    if self.camera.is_connected:
                        frame = self.camera.capture_frame()
                        if frame:
                            with self._lock:
                                self._last_frame = frame
                            
                            # Limit UI updates based on config
                            current_time = time.time()
                            if current_time - self._last_emit_time >= self._ui_frame_interval:
                                self.frame_ready.emit(frame)
                                self._last_emit_time = current_time
                    
                    # Frame-rate limiting sleep. The ZED grab call is blocking, so no sleep is needed.
                    if "ZED" not in self.camera.camera_id:
                        try:
                            # Use more efficient sleep timing for Linux
                            sleep_time = max(0.001, 1 / self.camera.fps if self.camera.fps > 0 else 0.03)
                            time.sleep(sleep_time)
                        except Exception as sleep_error:
                            print(f"Sleep error in FrameWorker for {self.camera.camera_id}: {sleep_error}")
                            break
                except Exception as e:
                    print(f"Error in FrameWorker for {self.camera.camera_id}: {e}")
                    try:
                        time.sleep(1)
                    except:
                        print(f"Critical error in FrameWorker for {self.camera.camera_id}, stopping thread")
                        break
        except Exception as e:
            camera_id = self.camera_config['camera_id']
            error_message = f"Failed to connect to {camera_id}: {e}"
            print(error_message)
            self.connection_status.emit(camera_id, False, str(e))
        finally:
            try:
                if self.camera and self.camera.is_connected:
                    self.camera.disconnect()
            except Exception as e:
                print(f"Error disconnecting {self.camera.camera_id}: {e}")

    def get_last_frame(self):
        """Get the last captured frame in a thread-safe way."""
        with self._lock:
            return self._last_frame

    def stop(self):
        """Stop the worker thread."""
        self.running = False

class PreviewWidget(QWidget):
    """A widget to display a single camera's preview with RGB and Depth."""

    def __init__(self, project_root: str, camera_id: str):
        super().__init__()
        self.camera_id = camera_id
        self.project_root = project_root

        # Load the UI file
        ui_file = os.path.join(self.project_root, "src", "gui", "ui", "preview_widget.ui")
        uic.loadUi(ui_file, self)

        self.setProperty("class", "camera-section")
        self.setMinimumSize(320, 240)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.camera_title.setText(camera_id)
        
        self.display_widgets = []
        display_types = ["RGB", "Depth"]
        if "ZED" in camera_id:
            display_types = ["RGB Left", "RGB Right", "Depth"]

        for display_type in display_types:
            display_widget = self.create_display_widget(display_type)
            self.display_widgets.append(display_widget)
            self.displays_layout.addWidget(display_widget)
        
        self.frame_number = 0
    
    def create_display_widget(self, display_type: str):
        ui_file = os.path.join(self.project_root, "src", "gui", "ui", "display_widget.ui")
        display_widget = uic.loadUi(ui_file)
        
        display_widget.display_label.setText(display_type)
        display_widget.display_label.setProperty("class", "display-label")
        display_widget.image_container.setProperty("class", "display-frame")
        
        # Store the image label for later access
        self.__setattr__(f"{display_type.lower().replace(' ', '_')}_label", display_widget.image_label)
        
        return display_widget

    def update_connection_status(self, is_connected: bool, message: str):
        self.status_text.setText(message)
        if is_connected:
            self.status_indicator.setProperty("class", "status-dot-connected")
        else:
            self.status_indicator.setProperty("class", "status-dot-disconnected")
        # Re-polish to apply style changes
        self.status_indicator.style().unpolish(self.status_indicator)
        self.status_indicator.style().polish(self.status_indicator)

    def update_frame(self, frame):
        if frame is None: return
        self.frame_number = frame.frame_number

        try:
            if "ZED" in frame.camera_id:
                if hasattr(self, 'rgb_left_label') and hasattr(frame, 'rgb_image_left') and frame.rgb_image_left is not None:
                    self._update_image(self.rgb_left_label, frame.rgb_image_left)
                if hasattr(self, 'rgb_right_label') and hasattr(frame, 'rgb_image_right') and frame.rgb_image_right is not None:
                    self._update_image(self.rgb_right_label, frame.rgb_image_right)
                if hasattr(self, 'depth_label') and hasattr(frame, 'depth_image') and frame.depth_image is not None:
                    self._update_image(self.depth_label, frame.depth_image, is_depth=True)
            else:
                if hasattr(self, 'rgb_label') and hasattr(frame, 'rgb_image') and frame.rgb_image is not None:
                    self._update_image(self.rgb_label, frame.rgb_image)
                if hasattr(self, 'depth_label') and hasattr(frame, 'depth_image') and frame.depth_image is not None:
                    self._update_image(self.depth_label, frame.depth_image, is_depth=True)
        except Exception as e:
            print(f"Error updating frame for {self.camera_id}: {e}")
            # Set error text on available labels
            if hasattr(self, 'rgb_left_label'):
                self.rgb_left_label.setText("Display Error")
            if hasattr(self, 'rgb_right_label'):
                self.rgb_right_label.setText("Display Error")
            if hasattr(self, 'rgb_label'):
                self.rgb_label.setText("Display Error")
            if hasattr(self, 'depth_label'):
                self.depth_label.setText("Display Error")

    def _update_image(self, label: QLabel, image: np.ndarray, is_depth: bool = False):
        if not isinstance(image, np.ndarray) or image.size == 0:
            label.setText("Invalid Frame")
            return
        
        try:
            # Use view instead of copy when possible for better performance
            image_copy = image if image.flags.c_contiguous else image.copy()

            if is_depth:
                # Use a fixed depth range (e.g., 0-4000mm) for stable normalization
                depth_min, depth_max = 0, 4000
                # Handle invalid values (NaN, inf) before normalization
                valid_mask = np.isfinite(image_copy)
                image_copy = np.where(valid_mask, image_copy, 0)
                # Normalize to 0-255 for colormap
                normalized_depth = np.clip(image_copy, depth_min, depth_max)
                normalized_depth = (normalized_depth - depth_min) * (255 / (depth_max - depth_min))
                # Ensure no invalid values before casting
                normalized_depth = np.nan_to_num(normalized_depth, nan=0.0, posinf=255.0, neginf=0.0)
                # Use in-place operations where possible
                depth_uint8 = normalized_depth.astype(np.uint8)
                image_copy = cv2.applyColorMap(depth_uint8, cv2.COLORMAP_JET)

            label_w, label_h = label.width(), label.height()
            # --- Key Fix: Prevent 0-size dimensions from being passed to cv2.resize() ---
            if label_w > 10 and label_h > 10:  # Skip if the UI is not laid out yet
                img_h, img_w = image_copy.shape[:2]
                aspect_ratio = img_w / img_h

                if label_w / label_h > aspect_ratio:
                    new_w = max(1, int(label_h * aspect_ratio))
                    new_h = label_h
                else:
                    new_w = label_w
                    new_h = max(1, int(label_w / aspect_ratio))
                
                # Only resize if necessary to save CPU
                if (new_w != img_w or new_h != img_h) and new_w > 0 and new_h > 0:
                    try:
                        resized_image = cv2.resize(
                            image_copy,
                            (new_w, new_h),
                            interpolation=cv2.INTER_LINEAR,  # Faster than INTER_AREA for downscaling
                        )
                    except cv2.error as e:
                        print(f'cv2.resize failed: {e}')
                        return  # Abandon this frame to prevent abort
                else:
                    resized_image = image_copy
            else:
                resized_image = image_copy

            # Optimize QImage creation
            if len(resized_image.shape) == 3:
                h, w, ch = resized_image.shape
                if ch == 3:
                    # Ensure RGB format and contiguous memory
                    if not resized_image.flags.c_contiguous:
                        resized_image = np.ascontiguousarray(resized_image)
                    fmt = QImage.Format.Format_RGB888
                    bytes_per_line = ch * w
                else:
                    fmt = QImage.Format.Format_RGBA8888
                    bytes_per_line = ch * w
                q_img = QImage(resized_image.data, w, h, bytes_per_line, fmt)
            else:
                h, w = resized_image.shape
                if not resized_image.flags.c_contiguous:
                    resized_image = np.ascontiguousarray(resized_image)
                q_img = QImage(resized_image.data, w, h, w, QImage.Format.Format_Grayscale8)

            pixmap = QPixmap.fromImage(q_img)
            label.setPixmap(pixmap)

        except Exception as e:
            print(f"Error updating frame for {self.camera_title.text()}: {e}")
            label.setText("Display Error")

class PreviewGrid(QWidget):
    """A grid of preview widgets that uses background threads for updates."""

    def __init__(self, project_root: str, device_manager):
        super().__init__()
        self.project_root = project_root
        self.device_manager = device_manager
        self.previews = {}
        self.workers = {}
        self.threads = []

        grid_layout = QGridLayout(self)
        grid_layout.setContentsMargins(10, 10, 10, 10)
        grid_layout.setSpacing(15)
        self.setLayout(grid_layout)

        camera_configs = self.device_manager.get_all_camera_configs()
        realsense_configs = sorted([c for c in camera_configs if "ZED" not in c['camera_id']], key=lambda cam: cam['camera_id'])
        zed_configs = [c for c in camera_configs if "ZED" in c['camera_id']]

        # Define the grid positions for RealSense cameras
        realsense_positions = [(0, 0), (0, 1), (1, 0), (1, 1)]

        # Place up to 4 RealSense cameras in their designated slots
        for i, cam_config in enumerate(realsense_configs[:4]):
            row, col = realsense_positions[i]
            self._setup_camera_preview(cam_config, grid_layout, row, col)

        # Place the ZED camera if it exists, in its designated slot
        if zed_configs:
            # The ZED camera is placed on the third row, spanning two columns
            self._setup_camera_preview(zed_configs[0], grid_layout, 2, 0, 1, 2)

        # Set stretch factors for columns and rows
        for i in range(2):
            grid_layout.setColumnStretch(i, 1)
        for i in range(3):
            grid_layout.setRowStretch(i, 1)

    def _setup_camera_preview(self, cam_config, layout, row, col, rowspan=1, colspan=1):
        camera_id = cam_config['camera_id']
        preview = PreviewWidget(self.project_root, camera_id)
        self.previews[camera_id] = preview
        layout.addWidget(preview, row, col, rowspan, colspan)
        
        thread = QThread()
        worker = FrameWorker(cam_config, self.device_manager.factory)
        self.workers[camera_id] = worker
        worker.moveToThread(thread)
        
        worker.frame_ready.connect(self.on_frame_ready)
        worker.connection_status.connect(self.on_connection_status)
        thread.started.connect(worker.run)
        
        self.threads.append((thread, worker))
        thread.start()

    def on_frame_ready(self, frame):
        if frame and frame.camera_id in self.previews:
            self.previews[frame.camera_id].update_frame(frame)

    def on_connection_status(self, camera_id: str, is_connected: bool, message: str):
        if camera_id in self.previews:
            self.previews[camera_id].update_connection_status(is_connected, message)

    def get_last_frames(self):
        return [w.get_last_frame() for w in self.workers.values() if w.get_last_frame()]

    def stop_threads(self):
        print("Stopping all frame workers...")
        # Signal all workers to stop
        for _, worker in self.threads:
            worker.stop()
        
        # Load timeout from config
        from src.services.config_service import ConfigService
        config = ConfigService()
        timeout_ms = config.thread_stop_timeout_ms
        
        # Wait for all threads to finish with configurable timeout
        for thread, worker in self.threads:
            thread.quit()
            if not thread.wait(timeout_ms):
                print(f"Thread for {worker.camera_config['camera_id']} timed out. Terminating.")
                thread.terminate()
                if not thread.wait(1000):  # Give 1 more second for termination
                    print(f"Force terminating thread for {worker.camera_config['camera_id']}")
        print("All frame workers stopped.")
