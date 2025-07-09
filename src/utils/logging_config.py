"""
Logging configuration for the MultiCamCollector application.

This module provides centralized logging setup with proper formatting,
file rotation, and stream redirection capabilities.
"""

import sys
import os
import logging
import time
from typing import Optional
from pathlib import Path


class StreamToLogger:
    """
    A class to redirect stream output (like stdout or stderr) to a logger.
    
    This allows capturing print statements and other stdout/stderr output
    into the application's logging system.
    """
    
    def __init__(self, logger: logging.Logger, level: int):
        self.logger = logger
        self.level = level
        self.linebuf = ''

    def write(self, buf: str) -> None:
        """Write buffer content to logger."""
        for line in buf.rstrip().splitlines():
            self.logger.log(self.level, line.rstrip())

    def flush(self) -> None:
        """Flush the stream (no-op for logger)."""
        pass


def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "logs",
    enable_console: bool = True,
    enable_file: bool = True,
    redirect_stdout: bool = True
) -> logging.Logger:
    """
    Setup application logging with file and console handlers.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory to store log files
        enable_console: Whether to enable console logging
        enable_file: Whether to enable file logging
        redirect_stdout: Whether to redirect stdout/stderr to logger
        
    Returns:
        Configured root logger
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Add file handler if enabled
    if enable_file:
        log_filename = f"multicam_{time.strftime('%Y-%m-%d_%H-%M-%S')}.log"
        file_handler = logging.FileHandler(
            log_path / log_filename,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)  # File gets all messages
        root_logger.addHandler(file_handler)
    
    # Add console handler if enabled
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        root_logger.addHandler(console_handler)
    
    # Redirect stdout and stderr to logger if requested
    if redirect_stdout:
        sys.stdout = StreamToLogger(root_logger, logging.INFO)
        sys.stderr = StreamToLogger(root_logger, logging.ERROR)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
