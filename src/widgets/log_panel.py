import os
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget

# Define project root and construct UI file path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UI_FILE = os.path.join(PROJECT_ROOT, "ui", "log_panel.ui")

class LogPanel(QWidget):
    """A panel to display log messages."""

    def __init__(self, project_root: str):
        super().__init__()
        ui_file = os.path.join(project_root, "ui", "log_panel.ui")
        uic.loadUi(ui_file, self)

    def add_log_message(self, message: str) -> None:
        """Add a message to the log panel."""
        self.log_text_edit.append(message)
