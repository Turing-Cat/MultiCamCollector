from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGridLayout
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt6.QtGui import QImage, QPixmap
import cv2
import numpy as np
import time
import threading
from devices.abstract_camera import AbstractCamera

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
    """A widget to display a single camera's preview."""

    def __init__(self, camera_id: str):
        super().__init__()

        # Set fixed size constraints for uniform appearance
        self.setMinimumSize(300, 200)
        self.setMaximumSize(400, 300)

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        self.camera_id_label = QLabel(camera_id)
        self.camera_id_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_id_label.setStyleSheet("font-weight: bold; padding: 2px;")
        layout.addWidget(self.camera_id_label)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid #ccc; background-color: #f0f0f0;")
        self.image_label.setMinimumSize(280, 160)
        layout.addWidget(self.image_label, 1)

    def update_frame(self, frame):
        """Update the displayed frame data."""
        if frame is None:
            self.image_label.setText("No Frame")
            return

        try:
            if not isinstance(frame.rgb_image, np.ndarray):
                self.image_label.setText("Invalid Frame Type")
                return

            rgb_image = frame.rgb_image
            if rgb_image is None or rgb_image.size == 0:
                self.image_label.setText("Empty Frame")
                return

            # Debug: Print frame info for troubleshooting (only for first few frames)
            if hasattr(self, '_frame_count'):
                self._frame_count += 1
            else:
                self._frame_count = 1
                print(f"First frame info for {self.camera_id_label.text()} - Shape: {rgb_image.shape}, dtype: {rgb_image.dtype}")

            if len(rgb_image.shape) == 3 and rgb_image.shape[2] >= 3:
                h, w = rgb_image.shape[:2]

                # ZED cameras typically output BGR format, convert to RGB for Qt
                if rgb_image.shape[2] == 4:  # BGRA format
                    rgb_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGRA2RGB)
                elif rgb_image.shape[2] == 3:  # BGR format
                    rgb_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2RGB)

                # Ensure the image is contiguous in memory
                rgb_image = np.ascontiguousarray(rgb_image)

                bytes_per_line = 3 * w
                q_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(q_img)

                if not pixmap.isNull():
                    # Scale to fit the image label while maintaining aspect ratio
                    label_size = self.image_label.size()
                    if label_size.width() > 0 and label_size.height() > 0:
                        scaled_pixmap = pixmap.scaled(
                            label_size,
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation
                        )
                        self.image_label.setPixmap(scaled_pixmap)
                    else:
                        # Fallback to a reasonable default size if label size is not available
                        scaled_pixmap = pixmap.scaled(
                            280, 160,
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation
                        )
                        self.image_label.setPixmap(scaled_pixmap)
                else:
                    self.image_label.setText("Invalid Image")
            else:
                self.image_label.setText(f"Unsupported Format: {rgb_image.shape}")

        except Exception as e:
            print(f"Error updating frame for {self.camera_id_label.text()}: {e}")
            self.image_label.setText("Display Error")

class PreviewGrid(QWidget):
    """A grid of preview widgets that uses background threads for updates."""

    def __init__(self, device_manager):
        super().__init__()
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
            preview = PreviewWidget(camera.camera_id)
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
