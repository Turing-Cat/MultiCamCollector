import sys
import os
import logging
import time
import faulthandler
from PyQt6.QtWidgets import QApplication

# Add project root to Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# Enable faulthandler before redirecting stdout/stderr
faulthandler.enable()

from src.controllers.main_window_controller import MainWindowController

# Logging Setup
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] - %(message)s")
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
log_filename = f"multicam_{time.strftime('%Y-%m-%d_%H-%M-%S')}.log"
file_handler = logging.FileHandler(os.path.join(log_dir, log_filename))
file_handler.setFormatter(log_formatter)
root_logger.addHandler(file_handler)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(log_formatter)
root_logger.addHandler(stream_handler)

class StreamToLogger:
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

if __name__ == "__main__":
    logging.info("Application starting...")
    app = QApplication(sys.argv)
    
    try:
        # Define project root and pass it to the controller
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        controller = MainWindowController(project_root)
        controller.show()
        sys.exit(app.exec())
    except Exception as e:
        logging.error("An unhandled exception occurred: %s", e, exc_info=True)
        sys.exit(1)