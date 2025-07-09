import os
import platform
from typing import Union

from PyQt6.QtCore import QObject
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtCore import Qt

from src.widgets.main_window_view import MainWindowView
from src.services import (
    DeviceManager,
    CaptureOrchestrator,
    StorageService,
    SequenceCounter,
)
from src.models import CaptureMetadata


def get_zed_sdk_path() -> Union[str, None]:
    """Return ZED SDK installation path based on the platform."""
    if platform.system() == "Windows":
        return os.environ.get("ZED_SDK_ROOT_DIR", "C:/Program Files (x86)/ZED SDK")
    if platform.system() == "Linux":
        return os.environ.get("ZED_SDK_ROOT_DIR", "/usr/local/zed")
    return None


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
        zed_sdk_path = get_zed_sdk_path()

        self.device_manager = DeviceManager(zed_sdk_path=zed_sdk_path)
        self.device_manager.discover_cameras()

        self.storage_service = StorageService(root_dir=storage_root)
        self.sequence_counter = SequenceCounter(storage_dir=storage_root)

        # -----------------------------
        # View Initialization
        # -----------------------------
        self.view = MainWindowView(
            project_root, self.device_manager, default_storage_path=storage_root
        )
        self.capture_orchestrator = CaptureOrchestrator(self.view.preview_grid)

        # -----------------------------
        # Initial State Setup
        # -----------------------------
        self._set_initial_metadata()

        # -----------------------------
        # Signal and Slot Connections
        # -----------------------------
        self._connect_signals()

    def _set_initial_metadata(self):
        """Set the initial metadata in the view."""
        initial_metadata: CaptureMetadata = self.view.metadata_panel.get_metadata()
        initial_metadata.sequence_number = self.sequence_counter.get_current()
        self.view.metadata_panel.set_metadata(initial_metadata)

    def _connect_signals(self):
        """Connect signals from the view to the controller's slots."""
        self.view.metadata_panel.capture_button.clicked.connect(self.on_capture)
        self.view.metadata_panel.sequence_number_edit.valueChanged.connect(
            self.on_sequence_changed
        )
        self.view.settings_panel.path_edit.textChanged.connect(self.on_storage_path_changed)

        QShortcut(QKeySequence(Qt.Key.Key_Space), self.view, self.on_capture)

    def show(self):
        """Show the main window."""
        self.view.show()

    # ------------------------------------------------------------------
    # Slot Methods
    # ------------------------------------------------------------------

    def on_capture(self):
        """Handle the capture button click."""
        metadata = self.view.metadata_panel.get_metadata()
        settings = self.view.settings_panel.get_settings()
        self.view.log_panel.add_log_message(f"Capturing with metadata: {metadata.to_dict()}")

        frames = self.capture_orchestrator.capture_all_frames()
        if frames:
            session_dir = self.storage_service.save(frames, metadata, settings)
            self.view.log_panel.add_log_message(
                f"Saved {len(frames)} frames to: {session_dir}"
            )

            if not self.view.metadata_panel.lock_checkbox.isChecked():
                self.sequence_counter.increment()
                metadata.sequence_number = self.sequence_counter.get_current()
                self.view.metadata_panel.set_metadata(metadata)
        else:
            self.view.log_panel.add_log_message("Capture failed. No frames received.")

    def on_sequence_changed(self, value: int):
        """Handle the sequence number change."""
        self.sequence_counter.set_current(value)

    def on_storage_path_changed(self, path: str):
        """Handle the storage path change."""
        self.storage_service.set_root_dir(path)
