from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QFormLayout, QComboBox, QLineEdit, QPushButton, QCheckBox
from models import LightingLevel, CaptureMetadata

class MetadataPanel(QWidget):
    """A panel for inputting and managing capture metadata."""

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        form_layout = QFormLayout()
        layout.addLayout(form_layout)

        self.lighting_combo = QComboBox()
        self.lighting_combo.addItems([level.value for level in LightingLevel])
        form_layout.addRow("Lighting Level:", self.lighting_combo)

        self.background_id_edit = QLineEdit("default_bg")
        form_layout.addRow("Background ID:", self.background_id_edit)

        self.sequence_number_edit = QLineEdit("1")
        form_layout.addRow("Sequence Number:", self.sequence_number_edit)

        self.lock_checkbox = QCheckBox("Lock Metadata")
        layout.addWidget(self.lock_checkbox)

        self.capture_button = QPushButton("Capture")
        layout.addWidget(self.capture_button)

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
