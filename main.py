import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QShortcut, QKeySequence
from gui import PreviewGrid, MetadataPanel, LogPanel, SettingsPanel
from services import DeviceManager, CaptureOrchestrator, StorageService, SequenceCounter
from models import CaptureMetadata

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-Camera Collector")
        self.setGeometry(100, 100, 1800, 1000)

        # Initialize services
        storage_root = "D:/Dataset"
        self.device_manager = DeviceManager()
        self.device_manager.discover_cameras()
        self.storage_service = StorageService(root_dir=storage_root)
        self.sequence_counter = SequenceCounter(storage_dir=storage_root)

        # Create UI components
        self.preview_grid = PreviewGrid(self.device_manager)
        self.capture_orchestrator = CaptureOrchestrator(self.preview_grid) # Pass the grid
        self.metadata_panel = MetadataPanel()
        self.log_panel = LogPanel()
        self.settings_panel = SettingsPanel(default_path=storage_root)

        # Set initial sequence number in UI
        initial_metadata = self.metadata_panel.get_metadata()
        initial_metadata.sequence_number = self.sequence_counter.get_current()
        self.metadata_panel.set_metadata(initial_metadata)

        # Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Left side (previews and logs)
        left_splitter = QSplitter(Qt.Orientation.Vertical)
        left_splitter.addWidget(self.preview_grid)
        left_splitter.addWidget(self.log_panel)
        left_splitter.setSizes([800, 200])

        # Right side (metadata, settings)
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.metadata_panel)
        right_layout.addWidget(self.settings_panel)
        right_layout.addStretch()
        
        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.addWidget(left_splitter)
        main_splitter.addWidget(right_widget)
        main_splitter.setSizes([1300, 500])
        
        main_layout.addWidget(main_splitter)

        # Connect signals
        self.metadata_panel.capture_button.clicked.connect(self.on_capture)
        self.metadata_panel.sequence_number_edit.textChanged.connect(self.on_sequence_changed)
        self.settings_panel.path_edit.textChanged.connect(self.on_storage_path_changed)

        # Spacebar shortcut for capture
        shortcut = QShortcut(QKeySequence(Qt.Key.Key_Space), self)
        shortcut.activated.connect(self.on_capture)

    def closeEvent(self, event):
        """Handle the main window close event."""
        self.preview_grid.stop_threads()
        super().closeEvent(event)

    def on_capture(self):
        """Handle the capture button click."""
        metadata = self.metadata_panel.get_metadata()
        settings = self.settings_panel.get_settings()
        
        self.log_panel.add_log_message(f"Capturing with metadata: {metadata.to_dict()}")

        frames = self.capture_orchestrator.capture_all_frames()
        if frames:
            session_dir = self.storage_service.save(frames, metadata, settings)
            self.log_panel.add_log_message(f"Saved {len(frames)} frames to: {session_dir}")
            
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
            pass

    def on_storage_path_changed(self, path: str):
        """Update the storage service with the new path."""
        self.storage_service.set_root_dir(path)


def main():
    """Main function to run the application."""
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.showMaximized()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
