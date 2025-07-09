import os
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QFileDialog

# Define project root and construct UI file path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UI_FILE = os.path.join(PROJECT_ROOT, "ui", "settings_panel.ui")

class SettingsPanel(QWidget):
    """A panel for configuring data saving settings."""

    def __init__(self, project_root: str, default_path="D:/Dataset"):
        super().__init__()
        ui_file = os.path.join(project_root, "ui", "settings_panel.ui")
        uic.loadUi(ui_file, self)

        self.path_edit.setText(default_path)
        self.browse_button.clicked.connect(self.browse_for_directory)

    def browse_for_directory(self):
        """Open a dialog to select a directory."""
        directory = QFileDialog.getExistingDirectory(self, "Select Storage Directory", self.path_edit.text())
        if directory:
            self.path_edit.setText(directory)

    def get_settings(self) -> dict:
        """Return the current settings."""
        return {
            "save_rgb": self.save_rgb_checkbox.isChecked(),
            "save_depth": self.save_depth_checkbox.isChecked(),
            "save_point_cloud": self.save_point_cloud_checkbox.isChecked(),
            "path": self.path_edit.text(),
        }
