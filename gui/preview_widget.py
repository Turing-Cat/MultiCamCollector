from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGridLayout
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt6.QtGui import QImage, QPixmap
import cv2
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
        self.setFixedSize(640, 480)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        self.camera_id_label = QLabel(camera_id)
        self.camera_id_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.camera_id_label)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.image_label, 1)

    def update_frame(self, frame):
        """Update the displayed frame data."""
        if frame is None:
            self.image_label.setText("No Frame")
            return
            
        rgb_image = frame.rgb_image
        if len(rgb_image.shape) == 3 and rgb_image.shape[2] == 3:
            h, w, _ = rgb_image.shape
            rgb_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2RGB)
            bytes_per_line = 3 * w
            q_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            
            scaled_pixmap = pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)

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
        layout.setContentsMargins(5, 5, 5, 5)
        
        cameras = self.device_manager.get_all_cameras()
        for i, camera in enumerate(cameras):
            row, col = divmod(i, 3)
            preview = PreviewWidget(camera.camera_id)
            self.previews[camera.camera_id] = preview
            layout.addWidget(preview, row, col)

            thread = QThread()
            worker = FrameWorker(camera)
            self.workers[camera.camera_id] = worker
            worker.moveToThread(thread)

            worker.frame_ready.connect(self.on_frame_ready)
            thread.started.connect(worker.run)
            
            self.threads.append((thread, worker))
            thread.start()

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
