import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout
from gui import PreviewGrid, MetadataPanel, LogPanel
from services import DeviceManager, CaptureOrchestrator, StorageService, SequenceCounter
from models import CaptureMetadata

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-Camera Collector")
        self.setGeometry(100, 100, 1600, 900)

        # Initialize services
        storage_root = "D:/Dataset"
        self.device_manager = DeviceManager()
        self.device_manager.discover_cameras()
        self.capture_orchestrator = CaptureOrchestrator(self.device_manager)
        self.storage_service = StorageService(root_dir=storage_root)
        self.sequence_counter = SequenceCounter(storage_dir=storage_root)

        # Create UI components
        self.preview_grid = PreviewGrid(self.device_manager)
        self.metadata_panel = MetadataPanel()
        self.log_panel = LogPanel()

        # Set initial sequence number in UI
        initial_metadata = self.metadata_panel.get_metadata()
        initial_metadata.sequence_number = self.sequence_counter.get_current()
        self.metadata_panel.set_metadata(initial_metadata)

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
        self.metadata_panel.sequence_number_edit.textChanged.connect(self.on_sequence_changed)

        # Start device monitoring
        self.device_manager.start_monitoring()

    def closeEvent(self, event):
        """Handle the main window close event."""
        self.device_manager.stop_monitoring()
        super().closeEvent(event)

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
                self.sequence_counter.increment()
                metadata.sequence_number = self.sequence_counter.get_current()
                self.metadata_panel.set_metadata(metadata)
        else:
            self.log_panel.add_log_message("Capture failed. No frames received.")

    def on_sequence_changed(self, text: str):
        """Handle manual changes to the sequence number."""
        try:
            new_sequence = int(text)
            self.sequence_counter.set_current(new_sequence)
        except ValueError:
            # Ignore non-integer input
            pass


def main():
    """Main function to run the application."""
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
