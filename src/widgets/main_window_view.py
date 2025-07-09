import os
from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import Qt

from src.widgets.preview_widget import PreviewGrid
from src.widgets.metadata_panel import MetadataPanel
from src.widgets.log_panel import LogPanel
from src.widgets.settings_panel import SettingsPanel

# Define project root and construct UI file path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UI_FILE = os.path.join(PROJECT_ROOT, "ui", "main_window.ui")

class MainWindowView(QMainWindow):
    """
    The main window view of the application.

    This class loads the UI from a .ui file and populates it with custom widgets.
    It does not contain any application logic.
    """

    def __init__(self, project_root: str, device_manager, default_storage_path) -> None:
        super().__init__()

        # Load the UI from the .ui file
        ui_file = os.path.join(project_root, "ui", "main_window.ui")
        uic.loadUi(ui_file, self)

        # -----------------------------
        # Create Custom Widgets
        # -----------------------------
        self.preview_grid = PreviewGrid(project_root, device_manager)
        self.metadata_panel = MetadataPanel(project_root)
        self.log_panel = LogPanel(project_root)
        self.settings_panel = SettingsPanel(project_root, default_path=default_storage_path)

        # -----------------------------
        # Populate UI Containers
        # -----------------------------
        # Main preview area
        self.camera_grid_layout.addWidget(self.preview_grid)

        # Right-side controls
        self.right_layout.addWidget(self.metadata_panel)
        self.right_layout.addWidget(self.settings_panel)
        self.right_layout.addStretch()

        # Right-side log panel
        self.log_layout.addWidget(self.log_panel)

        # -----------------------------
        # Adjust Splitter Sizes
        # -----------------------------
        self.main_splitter.setSizes([1400, 520])
        self.right_splitter.setSizes([800, 280])

        # -----------------------------
        # Window setup
        # -----------------------------
        self.setMinimumSize(1280, 720)
        self.setWindowState(self.windowState() | Qt.WindowState.WindowMaximized)

    def closeEvent(self, event):
        """Handle the window close event."""
        self.preview_grid.stop_threads()
        super().closeEvent(event)
