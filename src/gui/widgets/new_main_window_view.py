import os
from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow

from src.services import StorageService
from src.gui.widgets.preview_widget import PreviewGrid
from src.gui.widgets.controls_panel import ControlsPanel
from src.gui.widgets.log_panel import LogPanel

class NewMainWindowView(QMainWindow):
    def __init__(self, project_root: str, device_manager, storage_service: StorageService, default_storage_path):
        super().__init__()
        
        ui_file = os.path.join(project_root, "src", "gui", "ui", "new_main_window.ui")
        uic.loadUi(ui_file, self)

        # Load and apply stylesheet
        style_sheet_path = os.path.join(project_root, "src", "gui", "ui", "light_style.css")
        try:
            with open(style_sheet_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print(f"Stylesheet not found at {style_sheet_path}")

        # self.showMaximized()

        # Create the preview grid
        self.preview_grid = PreviewGrid(project_root, device_manager, storage_service)

        # Find the placeholder widget from the .ui file and its parent layout
        placeholder_widget = self.camera_grid_container
        parent_layout = placeholder_widget.parentWidget().layout()

        # Replace the placeholder with the actual preview grid
        parent_layout.replaceWidget(placeholder_widget, self.preview_grid)

        # Remove the placeholder from the layout and delete it
        placeholder_widget.setParent(None)
        placeholder_widget.deleteLater()

        self.controls_panel = ControlsPanel(parent=self, project_root=project_root)
        self.controls_layout.addWidget(self.controls_panel)

        self.log_panel = LogPanel(project_root)
        self.log_layout.addWidget(self.log_panel)

    def get_preview_grid(self):
        return self.preview_grid

    def get_controls_panel(self):
        return self.controls_panel

    def get_log_panel(self):
        return self.log_panel

    def closeEvent(self, event):
        self.preview_grid.stop_threads()
        super().closeEvent(event)
