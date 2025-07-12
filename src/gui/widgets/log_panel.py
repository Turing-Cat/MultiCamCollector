import os
from datetime import datetime
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget
from html import escape

class LogPanel(QWidget):
    """A panel to display log messages."""

    def __init__(self, project_root: str):
        super().__init__()
        
        if project_root is None:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        ui_file = os.path.join(project_root, "src", "gui", "ui", "log_panel.ui")
        uic.loadUi(ui_file, self)

    def add_log_message(self, message: str, level: str = "info") -> None:
        """Add a message to the log panel with styling based on log level."""
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        safe_message = escape(message)
        
        # Define colors for different levels
        color_map = {
            "error": "#d32f2f",      # Dark Red
            "warning": "#f57c00",    # Dark Orange
            "success": "#388e3c",    # Dark Green
            "info": "#191919"       # Almost Black
        }
        color = color_map.get(level, "#e0e0e0")
        
        html = f'<div style="color: {color}; margin-bottom: 5px;">' \
               f'<span style="font-weight: bold;">{timestamp}</span> ' \
               f'<span>{safe_message}</span>' \
               f'</div>'
        
        self.log_text_edit.append(html)
        
        # Scroll to bottom
        self.log_text_edit.verticalScrollBar().setValue(
            self.log_text_edit.verticalScrollBar().maximum()
        )