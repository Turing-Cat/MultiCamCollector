from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QFormLayout, QCheckBox, QLineEdit, QPushButton, QFileDialog

class SettingsPanel(QWidget):
    """A panel for configuring data saving settings."""

    def __init__(self, default_path="D:/Dataset"):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        # --- Data Saving Group ---
        saving_group = QGroupBox("Data Saving Settings")
        saving_layout = QFormLayout()
        saving_group.setLayout(saving_layout)
        layout.addWidget(saving_group)

        self.save_rgb_checkbox = QCheckBox()
        self.save_rgb_checkbox.setChecked(True)
        saving_layout.addRow("Save RGB Images:", self.save_rgb_checkbox)

        self.save_depth_checkbox = QCheckBox()
        self.save_depth_checkbox.setChecked(True)
        saving_layout.addRow("Save Depth Images:", self.save_depth_checkbox)

        self.save_point_cloud_checkbox = QCheckBox()
        saving_layout.addRow("Save Point Clouds:", self.save_point_cloud_checkbox)

        # --- Storage Path Group ---
        path_group = QGroupBox("Storage Path")
        path_layout = QVBoxLayout()
        path_group.setLayout(path_layout)
        layout.addWidget(path_group)

        self.path_edit = QLineEdit(default_path)
        path_layout.addWidget(self.path_edit)

        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_for_directory)
        path_layout.addWidget(browse_button)

        layout.addStretch()

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
