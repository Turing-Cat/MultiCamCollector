import os
from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QFileDialog, QAbstractSpinBox
from src.models.metadata import CaptureMetadata, LightingLevel
from src.models.settings import Settings


class ControlsPanel(QWidget):
    """
    A widget that contains all the controls for the application.
    It loads its UI from a .ui file and provides methods to get and set
    the user-configured metadata and settings.
    """

    lighting_level_changed = pyqtSignal(LightingLevel)

    def __init__(self, parent=None, project_root=None):
        super().__init__(parent)

        if project_root is None:
            project_root = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )

        ui_file = os.path.join(project_root, "src", "gui", "ui", "controls_panel.ui")
        uic.loadUi(ui_file, self)

        self.sequence_number_edit.setReadOnly(True)
        self.sequence_number_edit.setButtonSymbols(
            QAbstractSpinBox.ButtonSymbols.NoButtons
        )

        # Populate lighting combo box
        self.lighting_combo.clear()
        for item in LightingLevel:
            self.lighting_combo.addItem(item.value)

        # Connect signals to slots
        self.browse_button.clicked.connect(self.on_browse)
        self.lighting_combo.currentTextChanged.connect(
            lambda text: self.lighting_level_changed.emit(LightingLevel(text))
        )

    def on_browse(self):
        """Open a dialog to select a directory."""
        directory = QFileDialog.getExistingDirectory(self, "Select Storage Directory")
        if directory:
            self.path_edit.setText(directory)

    def get_metadata(self) -> CaptureMetadata:
        """Returns the current capture metadata from the UI."""
        return CaptureMetadata(
            lighting=LightingLevel(self.lighting_combo.currentText()),
            background_id=self.background_id_edit.text(),
            sequence_number=self.sequence_number_edit.value(),
        )

    def set_metadata(self, metadata: CaptureMetadata):
        """Sets the UI with the given capture metadata."""
        self.lighting_combo.setCurrentText(metadata.lighting.value)
        self.background_id_edit.setText(metadata.background_id)
        self.sequence_number_edit.setValue(metadata.sequence_number)

    def get_settings(self) -> Settings:
        """Returns the current settings from the UI."""
        return Settings(
            save_rgb=self.save_rgb_checkbox.isChecked(),
            save_depth=self.save_depth_checkbox.isChecked(),
            save_raw_depth=self.save_raw_depth_checkbox.isChecked(),
            save_point_cloud=self.save_point_cloud_checkbox.isChecked(),
            lock_metadata=self.lock_checkbox.isChecked(),
            path=self.path_edit.text(),
        )

    def set_settings(self, settings: Settings):
        """Sets the UI with the given settings."""
        self.save_rgb_checkbox.setChecked(settings.save_rgb)
        self.save_depth_checkbox.setChecked(settings.save_depth)
        self.save_raw_depth_checkbox.setChecked(settings.save_raw_depth)
        self.save_point_cloud_checkbox.setChecked(settings.save_point_cloud)
        self.lock_checkbox.setChecked(settings.lock_metadata)
        self.path_edit.setText(settings.path)
