import os
import platform
import time
from typing import Union

from PyQt6.QtCore import QObject, QThread, pyqtSignal, Qt
from PyQt6.QtGui import QShortcut, QKeySequence

from src.gui.widgets.new_main_window_view import NewMainWindowView
from src.services import (
    DeviceManager,
    CaptureOrchestrator,
    StorageService,
    SequenceCounter,
)
from src.models import CaptureMetadata, Settings, LightingLevel


class CameraSettingsWorker(QObject):
    """Worker to apply camera settings in a separate thread."""

    finished = pyqtSignal(str)

    def __init__(self, device_manager: DeviceManager):
        super().__init__()
        self.device_manager = device_manager

    def set_lighting_level(self, level: LightingLevel):
        """Simulates setting the lighting level on the cameras."""
        self.finished.emit(f"Setting lighting level to {level.value}...")
        # Here you would have the actual logic to control the camera hardware.
        # Reduced sleep time for better responsiveness on Linux
        time.sleep(0.5)
        self.finished.emit(f"Lighting level set to {level.value}.")


class MainWindowController(QObject):
    """
    The main window controller of the application.

    This class is responsible for handling application logic, connecting signals
    and slots, and managing the interaction between the view and the models.
    """

    def __init__(self, project_root: str) -> None:
        super().__init__()
        self.project_root = project_root

        # -----------------------------
        # Services Initialization
        # -----------------------------
        storage_root = os.path.join(os.path.dirname(project_root), "the-dataset")
        self.device_manager = DeviceManager()
        self.device_manager.discover_cameras()

        self.storage_service = StorageService(root_dir=storage_root)
        self.sequence_counter = SequenceCounter(storage_dir=storage_root)

        # -----------------------------
        # View Initialization
        # -----------------------------
        self.view = NewMainWindowView(
            project_root, self.device_manager, self.storage_service, default_storage_path=storage_root
        )
        self.capture_orchestrator = CaptureOrchestrator(self.view.preview_grid)

        # -----------------------------
        # Worker Thread for Camera Settings
        # -----------------------------
        self.camera_settings_thread = QThread()
        self.camera_settings_worker = CameraSettingsWorker(self.device_manager)
        self.camera_settings_worker.moveToThread(self.camera_settings_thread)
        self.camera_settings_thread.start()

        # -----------------------------
        # Initial State Setup
        # -----------------------------
        self._set_initial_metadata()
        self._set_initial_settings()

        # -----------------------------
        # Signal and Slot Connections
        # -----------------------------
        self._connect_signals()

    def _set_initial_metadata(self):
        """Set the initial metadata in the view."""
        initial_metadata: CaptureMetadata = self.view.controls_panel.get_metadata()
        initial_metadata.sequence_number = self.sequence_counter.get_current()
        self.view.controls_panel.set_metadata(initial_metadata)

    def _set_initial_settings(self):
        """Set the initial settings in the view."""
        initial_settings = Settings(path=self.storage_service.get_root_dir())
        self.view.controls_panel.set_settings(initial_settings)

    def _connect_signals(self):
        """Connect signals from the view to the controller's slots."""
        self.view.controls_panel.capture_button.clicked.connect(self.on_capture)
        self.view.controls_panel.path_edit.textChanged.connect(
            self.on_storage_path_changed
        )
        self.view.controls_panel.lighting_level_changed.connect(
            self.camera_settings_worker.set_lighting_level
        )
        self.camera_settings_worker.finished.connect(
            self.view.log_panel.add_log_message
        )

        QShortcut(QKeySequence(Qt.Key.Key_Space), self.view, self.on_capture)

    def show(self):
        """Show the main window."""
        self.view.show()

    def on_capture(self):
        """Handle the capture button click."""
        metadata = self.view.controls_panel.get_metadata()
        settings = self.view.controls_panel.get_settings()
        self.view.log_panel.add_log_message(
            f"Capturing with metadata: {metadata.to_dict()}"
        )

        frames = self.capture_orchestrator.capture_all_frames()
        if frames:
            session_dir = self.storage_service.save(frames, metadata, settings)
            self.view.log_panel.add_log_message(
                f"Saved {len(frames)} frames to: {session_dir}"
            )

            # Always increment sequence number after successful capture
            # lock_metadata only affects saving options, not sequence numbering
            self.sequence_counter.increment()
            metadata.sequence_number = self.sequence_counter.get_current()
            self.view.controls_panel.set_metadata(metadata)
        else:
            self.view.log_panel.add_log_message("Capture failed. No frames received.")

    def on_storage_path_changed(self, path: str):
        """Handle the storage path change."""
        self.storage_service.set_root_dir(path)
