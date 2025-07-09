import sys
import os
import logging
import time
from PyQt6.QtWidgets import QApplication

from src.controllers.main_window_controller import MainWindowController

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
# Entrypoint
# -----------------------------------------------------------------------------

def main() -> None:
    logging.info("Application starting...")
    app = QApplication(sys.argv)
    
    # Define project root and pass it to the controller
    project_root = os.path.dirname(os.path.abspath(__file__))
    controller = MainWindowController(project_root)
    
    controller.show()
    exit_code = app.exec()
    logging.info(f"Application exiting with code {exit_code}.")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
