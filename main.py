import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout
from gui import PreviewGrid, MetadataPanel, LogPanel
from services import DeviceManager, CaptureOrchestrator, StorageService
from models import CaptureMetadata

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-Camera Collector")
        self.setGeometry(100, 100, 1600, 900)

        # Initialize services
        self.device_manager = DeviceManager()
        self.device_manager.discover_cameras()
        self.capture_orchestrator = CaptureOrchestrator(self.device_manager)
        self.storage_service = StorageService(root_dir="D:/Dataset")

        # Create UI components
        self.preview_grid = PreviewGrid([camera.camera_id for camera in self.device_manager.get_all_cameras()])
        self.metadata_panel = MetadataPanel()
        self.log_panel = LogPanel()

        # Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.preview_grid)
        left_layout.addWidget(self.log_panel)

        main_layout.addLayout(left_layout, stretch=3)
        main_layout.addWidget(self.metadata_panel, stretch=1)

        # Connect signals
        self.metadata_panel.capture_button.clicked.connect(self.on_capture)

    def on_capture(self):
        """Handle the capture button click."""
        metadata = self.metadata_panel.get_metadata()
        self.log_panel.add_log_message(f"Capturing with metadata: {metadata.to_dict()}")

        frames = self.capture_orchestrator.capture_all_frames()
        if frames:
            self.storage_service.save(frames, metadata)
            self.log_panel.add_log_message(f"Saved {len(frames)} frames.")
            
            # Increment sequence number
            if not self.metadata_panel.lock_checkbox.isChecked():
                metadata.sequence_number += 1
                self.metadata_panel.set_metadata(metadata)
        else:
            self.log_panel.add_log_message("Capture failed. No frames received.")


def main():
    """Main function to run the application."""
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
