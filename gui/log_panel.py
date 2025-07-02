from PyQt6.QtWidgets import QWidget, QTextEdit, QVBoxLayout

class LogPanel(QWidget):
    """A panel to display log messages."""

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)
        layout.addWidget(self.log_text_edit)

    def add_log_message(self, message: str) -> None:
        """Add a message to the log panel."""
        self.log_text_edit.append(message)
