import os
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGridLayout
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt6.QtGui import QImage, QPixmap
import cv2
import numpy as np
import time
import threading
from src.services.abstract_camera import AbstractCamera

# Define project root and construct UI file path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UI_FILE = os.path.join(PROJECT_ROOT, "ui", "preview_widget.ui")

class FrameWorker(QObject):
    """Worker to fetch frames from a camera in a background thread."""
    frame_ready = pyqtSignal(object)
    
    def __init__(self, camera: AbstractCamera):
        super().__init__()
        self.camera = camera
        self.running = True
        self._lock = threading.Lock()
        self._last_frame = None

    def run(self):
        """Continuously fetch frames from the camera."""
        while self.running:
            try:
                if self.camera.is_connected:
                    frame = self.camera.capture_frame()
                    if frame:
                        with self._lock:
                            self._last_frame = frame
                        self.frame_ready.emit(frame)
                time.sleep(0.03) # ~30 FPS
            except Exception as e:
                print(f"Error in FrameWorker for {self.camera.camera_id}: {e}")
                time.sleep(1)

    def get_last_frame(self):
        """Get the last captured frame in a thread-safe way."""
        with self._lock:
            return self._last_frame

class PreviewWidget(QWidget):
    """A widget to display a single camera's preview with RGB and Depth."""

    def __init__(self, project_root: str, camera_id: str):
        super().__init__()
        ui_file = os.path.join(project_root, "ui", "preview_widget.ui")
        uic.loadUi(ui_file, self)
        self.camera_id_label.setText(camera_id)
        self.setFixedSize(480, 360)

    def update_frame(self, frame):
        """Update the displayed frame data for both RGB and Depth."""
        if frame is None:
            self.rgb_left_image_label.setText("No Frame")
            self.depth_image_label.setText("No Frame")
            if hasattr(self, 'rgb_right_image_label'):
                self.rgb_right_image_label.setText("No Frame")
            return

        # Update RGB Image
        self._update_image(self.rgb_left_image_label, frame.rgb_image, "RGB")

        # Update Depth Image
        self._update_image(self.depth_image_label, frame.depth_image, "Depth")

        # Update Right RGB image if it exists
        if frame.rgb_image_right is not None:
            if hasattr(self, 'rgb_right_image_label'):
                self.rgb_right_image_label.show()
                self._update_image(self.rgb_right_image_label, frame.rgb_image_right, "RGB")
        else:
            if hasattr(self, 'rgb_right_image_label'):
                self.rgb_right_image_label.hide()

    def _update_image(self, label: QLabel, image: np.ndarray, image_type: str):
        """Update the image label."""
        if not isinstance(image, np.ndarray) or image.size == 0:
            label.setText(f"Invalid {image_type} Frame")
            return
        
        try:
            if image_type == "Depth":
                # Normalize depth map for visualization
                image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
                image = cv2.applyColorMap(image, cv2.COLORMAP_JET)

            h, w, ch = image.shape
            if ch == 4:
                image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
            elif ch == 3:
                 image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            q_img = QImage(image.data, w, h, ch * w, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            label.setPixmap(pixmap.scaled(
                label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
        except Exception as e:
            print(f"Error updating {image_type} frame for {self.camera_id_label.text()}: {e}")
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

        layout = QGridLayout()
        self.setLayout(layout)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        cameras = self.device_manager.get_all_cameras()
        if not cameras:
            return

        # --- Optimized Layout for Multiple Cameras ---
        num_cameras = len(cameras)

        # Define optimal grid arrangements for different camera counts
        if num_cameras <= 2:
            num_cols, num_rows = 2, 1
        elif num_cameras <= 4:
            num_cols, num_rows = 2, 2
        elif num_cameras == 5:
            # For 5 cameras, use 3x2 grid with cameras arranged as:
            # [1] [2] [3]
            # [4] [5] [ ]
            num_cols, num_rows = 3, 2
        elif num_cameras <= 6:
            num_cols, num_rows = 3, 2
        elif num_cameras <= 9:
            num_cols, num_rows = 3, 3
        else:
            # For more cameras, use a more square-like arrangement
            num_cols = int(np.ceil(np.sqrt(num_cameras)))
            num_rows = int(np.ceil(num_cameras / num_cols))

        # Create and position preview widgets
        for i, camera in enumerate(cameras):
            row, col = divmod(i, num_cols)
            preview = PreviewWidget(self.project_root, camera.camera_id)
            self.previews[camera.camera_id] = preview
            layout.addWidget(preview, row, col)

            # --- Worker Thread Setup ---
            thread = QThread()
            worker = FrameWorker(camera)
            self.workers[camera.camera_id] = worker
            worker.moveToThread(thread)

            worker.frame_ready.connect(self.on_frame_ready)
            thread.started.connect(worker.run)

            self.threads.append((thread, worker))
            thread.start()

        # --- Configure Grid Stretching ---
        # Set uniform stretch factors for all rows and columns
        for r in range(num_rows):
            layout.setRowStretch(r, 1)
        for c in range(num_cols):
            layout.setColumnStretch(c, 1)

        # Center the grid content
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def on_frame_ready(self, frame):
        """Slot to receive a frame and update the corresponding preview."""
        if frame and frame.camera_id in self.previews:
            self.previews[frame.camera_id].update_frame(frame)

    def get_last_frames(self):
        """Get the last frame from each worker."""
        frames = []
        for worker in self.workers.values():
            frame = worker.get_last_frame()
            if frame:
                frames.append(frame)
        return frames

    def stop_threads(self):
        """Stop all background threads."""
        for thread, worker in self.threads:
            worker.running = False
            thread.quit()
            thread.wait()
