import os
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget
from src.models.metadata import LightingLevel, CaptureMetadata

# Define project root and construct UI file path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UI_FILE = os.path.join(PROJECT_ROOT, "ui", "metadata_panel.ui")

class MetadataPanel(QWidget):
    """A panel for inputting and managing capture metadata."""

    def __init__(self, project_root: str):
        super().__init__()
        ui_file = os.path.join(project_root, "ui", "metadata_panel.ui")
        uic.loadUi(ui_file, self)

        self.lighting_combo.addItems([level.value for level in LightingLevel])
        self.background_id_edit.setText("default_bg")
        self.sequence_number_edit.setText("1")

    def get_metadata(self) -> CaptureMetadata:
        """Get the current metadata from the panel."""
        return CaptureMetadata(
            lighting=LightingLevel(self.lighting_combo.currentText()),
            background_id=self.background_id_edit.text(),
            sequence_number=int(self.sequence_number_edit.text()),
        )

    def set_metadata(self, metadata: CaptureMetadata) -> None:
        """Set the metadata in the panel."""
        self.lighting_combo.setCurrentText(metadata.lighting.value)
        self.background_id_edit.setText(metadata.background_id)
        self.sequence_number_edit.setText(str(metadata.sequence_number))
