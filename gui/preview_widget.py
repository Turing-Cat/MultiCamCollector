from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGridLayout
from PyQt6.QtCore import Qt

class PreviewWidget(QWidget):
    """A widget to display a single camera's preview."""

    def __init__(self, camera_id: str):
        super().__init__()
        self.setMinimumSize(320, 240)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.camera_id_label = QLabel(camera_id)
        self.camera_id_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.camera_id_label)

class PreviewGrid(QWidget):
    """A grid of preview widgets."""

    def __init__(self, camera_ids: list[str]):
        super().__init__()

        layout = QGridLayout()
        self.setLayout(layout)

        self.previews = {}
        for i, camera_id in enumerate(camera_ids):
            row, col = divmod(i, 2)
            preview = PreviewWidget(camera_id)
            self.previews[camera_id] = preview
            layout.addWidget(preview, row, col)
