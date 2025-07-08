import sys
import platform
import os
import logging
import time
from typing import Union
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QSplitter,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QShortcut, QKeySequence

from gui import PreviewGrid, MetadataPanel, LogPanel, SettingsPanel
from services import (
    DeviceManager,
    CaptureOrchestrator,
    StorageService,
    SequenceCounter,
)
from models import CaptureMetadata

# -----------------------------------------------------------------------------
# Logging Setup
# -----------------------------------------------------------------------------

# 1. Create logs directory if it doesn't exist
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# 2. Create a logger
log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] - %(message)s")
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# 3. Create a file handler
log_filename = f"multicam_{time.strftime('%Y-%m-%d_%H-%M-%S')}.log"
file_handler = logging.FileHandler(os.path.join(log_dir, log_filename))
file_handler.setFormatter(log_formatter)
root_logger.addHandler(file_handler)

# 4. Create a stream handler to also print to console
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(log_formatter)
root_logger.addHandler(stream_handler)

# 5. Redirect stdout and stderr to the logger
class StreamToLogger:
    """
    A class to redirect stream output (like stdout or stderr) to a logger.
    """
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.level, line.rstrip())

    def flush(self):
        pass

sys.stdout = StreamToLogger(root_logger, logging.INFO)
sys.stderr = StreamToLogger(root_logger, logging.ERROR)


# -----------------------------------------------------------------------------
# Helper
# -----------------------------------------------------------------------------

def get_zed_sdk_path() -> Union[str, None]:
    """Return ZED SDK 安装路径，按平台区分。"""
    if platform.system() == "Windows":
        return os.environ.get("ZED_SDK_ROOT_DIR", "C:/Program Files (x86)/ZED SDK")
    if platform.system() == "Linux":
        return os.environ.get("ZED_SDK_ROOT_DIR", "/usr/local/zed")
    return None


# -----------------------------------------------------------------------------
# Main Window
# -----------------------------------------------------------------------------

class MainWindow(QMainWindow):
    """应用主窗口。"""

    def __init__(self) -> None:
        super().__init__()

        # -----------------------------
        # Window flags / 状态设置
        # -----------------------------
        # 1. 保留系统装饰；2. 显示最大化 / 最小化按钮；3. 允许移动 / 缩放。
        flags = self.windowFlags()
        flags |= (
            Qt.WindowType.WindowMinMaxButtonsHint
            | Qt.WindowType.WindowSystemMenuHint
            | Qt.WindowType.WindowCloseButtonHint
            | Qt.WindowType.WindowTitleHint
        )
        self.setWindowFlags(flags)

        self.setWindowTitle("Multi-Camera Collector")

        # 仅作为 *fallback*，真正启动时会被 WindowMaximized 覆盖。
        self.resize(1800, 1000)
        self.setMinimumSize(800, 600)

        # -----------------------------
        # Services 初始化
        # -----------------------------
        storage_root = "D:/Dataset"  # TODO: 可在 SettingsPanel 中修改
        zed_sdk_path = get_zed_sdk_path()

        self.device_manager = DeviceManager(zed_sdk_path=zed_sdk_path)
        self.device_manager.discover_cameras()

        self.storage_service = StorageService(root_dir=storage_root)
        self.sequence_counter = SequenceCounter(storage_dir=storage_root)

        # -----------------------------
        # UI 组件
        # -----------------------------
        self.preview_grid = PreviewGrid(self.device_manager)
        self.capture_orchestrator = CaptureOrchestrator(self.preview_grid)
        self.metadata_panel = MetadataPanel()
        self.log_panel = LogPanel()
        self.settings_panel = SettingsPanel(default_path=storage_root)

        # 初始序号写入 UI
        initial_metadata: CaptureMetadata = self.metadata_panel.get_metadata()
        initial_metadata.sequence_number = self.sequence_counter.get_current()
        self.metadata_panel.set_metadata(initial_metadata)

        # -----------------------------
        # 布局
        # -----------------------------
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QHBoxLayout(central)

        # 左侧：预览 + 日志
        left_split = QSplitter(Qt.Orientation.Vertical)
        left_split.addWidget(self.preview_grid)
        left_split.addWidget(self.log_panel)
        left_split.setSizes([800, 200])

        # 右侧：元数据 + 设置
        right_box = QVBoxLayout()
        right_box.addWidget(self.metadata_panel)
        right_box.addWidget(self.settings_panel)
        right_box.addStretch()
        right_widget = QWidget()
        right_widget.setLayout(right_box)

        # 总分隔
        main_split = QSplitter(Qt.Orientation.Horizontal)
        main_split.addWidget(left_split)
        main_split.addWidget(right_widget)
        main_split.setSizes([1300, 500])
        root_layout.addWidget(main_split)

        # -----------------------------
        # 信号 / 快捷键
        # -----------------------------
        self.metadata_panel.capture_button.clicked.connect(self.on_capture)
        self.metadata_panel.sequence_number_edit.textChanged.connect(
            self.on_sequence_changed
        )
        self.settings_panel.path_edit.textChanged.connect(self.on_storage_path_changed)

        QShortcut(QKeySequence(Qt.Key.Key_Space), self, self.on_capture)

        # -----------------------------
        # 启动即最大化
        # -----------------------------
        # 直接设置窗口状态，而不是 showMaximized → 避免在某些 WM 上第二次 show 被忽略
        self.setWindowState(self.windowState() | Qt.WindowState.WindowMaximized)

    # ------------------------------------------------------------------
    # 事件处理
    # ------------------------------------------------------------------

    def closeEvent(self, event):
        """窗口关闭时，停止预览线程。"""
        self.preview_grid.stop_threads()
        super().closeEvent(event)

    # -----------------------------
    # Capture 流程
    # -----------------------------

    def on_capture(self):
        metadata = self.metadata_panel.get_metadata()
        settings = self.settings_panel.get_settings()
        self.log_panel.add_log_message(f"Capturing with metadata: {metadata.to_dict()}")

        frames = self.capture_orchestrator.capture_all_frames()
        if frames:
            session_dir = self.storage_service.save(frames, metadata, settings)
            self.log_panel.add_log_message(
                f"Saved {len(frames)} frames to: {session_dir}"
            )

            if not self.metadata_panel.lock_checkbox.isChecked():
                self.sequence_counter.increment()
                metadata.sequence_number = self.sequence_counter.get_current()
                self.metadata_panel.set_metadata(metadata)
        else:
            self.log_panel.add_log_message("Capture failed. No frames received.")

    def on_sequence_changed(self, text: str):
        try:
            new_seq = int(text)
            self.sequence_counter.set_current(new_seq)
        except ValueError:
            # 非数字输入时忽略
            pass

    def on_storage_path_changed(self, path: str):
        self.storage_service.set_root_dir(path)


# -----------------------------------------------------------------------------
# Entrypoint
# -----------------------------------------------------------------------------

def main() -> None:
    logging.info("Application starting...")
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()  # WindowState 已在 __init__ 设置为 Maximized
    exit_code = app.exec()
    logging.info(f"Application exiting with code {exit_code}.")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
