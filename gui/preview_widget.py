from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGridLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap
import cv2

class PreviewWidget(QWidget):
    """A widget to display a single camera's preview."""

    def __init__(self, camera_id: str):
        super().__init__()
        # 固定预览窗口尺寸为640x480像素
        self.setFixedSize(640, 480)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 相机ID标签
        self.camera_id_label = QLabel(camera_id)
        self.camera_id_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.camera_id_label)
        
        # 图像显示区域
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.image_label, 1)

    def update_frame(self, frame):
        """更新显示的帧数据"""
        # 将numpy数组转换为QPixmap
        rgb_image = frame.rgb_image
        if len(rgb_image.shape) == 3 and rgb_image.shape[2] == 3:
            h, w, _ = rgb_image.shape
            # OpenCV使用BGR格式，需要转换为RGB
            rgb_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2RGB)
            bytes_per_line = 3 * w
            q_img = QImage(rgb_image.data, w, h, bytes_per_line,
                         QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            
            # 保持比例缩放
            scaled_pixmap = pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)

class PreviewGrid(QWidget):
    """A grid of preview widgets."""

    def __init__(self, device_manager):
        super().__init__()
        self.device_manager = device_manager
        cameras = device_manager.get_all_cameras()
        
        layout = QGridLayout()
        self.setLayout(layout)
        layout.setContentsMargins(5, 5, 5, 5)
        
        self.previews = {}
        for i, camera in enumerate(cameras):
            row, col = divmod(i, 3)  # 3列布局
            preview = PreviewWidget(camera.camera_id)
            self.previews[camera.camera_id] = preview
            layout.addWidget(preview, row, col)

        # 设置定时器更新画面
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_all_previews)
        self.timer.start(33)  # ~30fps

    def update_all_previews(self):
        """更新所有预览窗口的画面"""
        for camera in self.device_manager.get_all_cameras():
            try:
                frame = camera.capture_frame()
                if camera.camera_id in self.previews:
                    # 直接使用Frame对象的rgb_image属性
                    self.previews[camera.camera_id].update_frame(frame)
            except Exception as e:
                print(f"Error updating preview for {camera.camera_id}: {e}")
