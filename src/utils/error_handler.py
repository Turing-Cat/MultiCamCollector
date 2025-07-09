"""
Error handling utilities for MultiCamCollector.

This module provides utilities for handling errors gracefully
and presenting user-friendly error messages.
"""

import traceback
from typing import Optional, Dict, Any, Callable
from functools import wraps

from PyQt6.QtWidgets import QMessageBox, QWidget
from PyQt6.QtCore import QObject, pyqtSignal

from src.services.exceptions import (
    MultiCamError, DeviceError, CameraError, CaptureError, 
    StorageError, ConfigurationError, ValidationError, SynchronizationError
)
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class ErrorHandler(QObject):
    """
    Centralized error handler for the application.
    
    This class provides methods for handling different types of errors
    and presenting appropriate user feedback.
    """
    
    # Signals for error notifications
    error_occurred = pyqtSignal(str, str)  # title, message
    warning_occurred = pyqtSignal(str, str)  # title, message
    
    def __init__(self, parent_widget: Optional[QWidget] = None):
        """
        Initialize the error handler.
        
        Args:
            parent_widget: Parent widget for message boxes
        """
        super().__init__()
        self._parent_widget = parent_widget
    
    def handle_error(self, error: Exception, context: str = "", show_dialog: bool = True) -> None:
        """
        Handle an error with appropriate logging and user notification.
        
        Args:
            error: Exception that occurred
            context: Additional context about where the error occurred
            show_dialog: Whether to show a dialog to the user
        """
        error_info = self._analyze_error(error, context)
        
        # Log the error
        logger.error(f"{error_info['title']}: {error_info['message']}", exc_info=True)
        
        # Emit signal for other components
        self.error_occurred.emit(error_info['title'], error_info['message'])
        
        # Show dialog if requested
        if show_dialog and self._parent_widget:
            self._show_error_dialog(error_info['title'], error_info['message'], error_info['details'])
    
    def handle_warning(self, message: str, title: str = "Warning", show_dialog: bool = True) -> None:
        """
        Handle a warning with appropriate logging and user notification.
        
        Args:
            message: Warning message
            title: Warning title
            show_dialog: Whether to show a dialog to the user
        """
        logger.warning(f"{title}: {message}")
        
        # Emit signal for other components
        self.warning_occurred.emit(title, message)
        
        # Show dialog if requested
        if show_dialog and self._parent_widget:
            self._show_warning_dialog(title, message)
    
    def _analyze_error(self, error: Exception, context: str) -> Dict[str, str]:
        """
        Analyze an error and generate user-friendly information.
        
        Args:
            error: Exception to analyze
            context: Additional context
            
        Returns:
            Dictionary with title, message, and details
        """
        if isinstance(error, ValidationError):
            return {
                'title': 'Validation Error',
                'message': f"Invalid input: {error.message}",
                'details': str(error.details) if error.details else ""
            }
        
        elif isinstance(error, CameraError):
            device_id = error.details.get('device_id', 'Unknown')
            return {
                'title': 'Camera Error',
                'message': f"Camera '{device_id}' error: {error.message}",
                'details': self._format_error_details(error.details)
            }
        
        elif isinstance(error, DeviceError):
            device_id = error.details.get('device_id', 'Unknown')
            return {
                'title': 'Device Error',
                'message': f"Device '{device_id}' error: {error.message}",
                'details': self._format_error_details(error.details)
            }
        
        elif isinstance(error, CaptureError):
            camera_id = error.details.get('camera_id', 'Unknown')
            return {
                'title': 'Capture Error',
                'message': f"Capture failed for camera '{camera_id}': {error.message}",
                'details': self._format_error_details(error.details)
            }
        
        elif isinstance(error, StorageError):
            path = error.details.get('path', 'Unknown')
            return {
                'title': 'Storage Error',
                'message': f"Storage error at '{path}': {error.message}",
                'details': self._format_error_details(error.details)
            }
        
        elif isinstance(error, ConfigurationError):
            config_key = error.details.get('config_key', 'Unknown')
            return {
                'title': 'Configuration Error',
                'message': f"Configuration error for '{config_key}': {error.message}",
                'details': self._format_error_details(error.details)
            }
        
        elif isinstance(error, SynchronizationError):
            return {
                'title': 'Synchronization Error',
                'message': f"Frame synchronization failed: {error.message}",
                'details': self._format_error_details(error.details)
            }
        
        elif isinstance(error, MultiCamError):
            return {
                'title': 'Application Error',
                'message': error.message,
                'details': self._format_error_details(error.details)
            }
        
        else:
            # Generic error
            error_type = type(error).__name__
            return {
                'title': f'{error_type}',
                'message': f"{context + ': ' if context else ''}{str(error)}",
                'details': traceback.format_exc()
            }
    
    def _format_error_details(self, details: Dict[str, Any]) -> str:
        """Format error details for display."""
        if not details:
            return ""
        
        formatted = []
        for key, value in details.items():
            formatted.append(f"{key}: {value}")
        
        return "\n".join(formatted)
    
    def _show_error_dialog(self, title: str, message: str, details: str = "") -> None:
        """Show an error dialog to the user."""
        try:
            msg_box = QMessageBox(self._parent_widget)
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            
            if details:
                msg_box.setDetailedText(details)
            
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()
            
        except Exception as e:
            logger.error(f"Error showing error dialog: {e}")
    
    def _show_warning_dialog(self, title: str, message: str) -> None:
        """Show a warning dialog to the user."""
        try:
            msg_box = QMessageBox(self._parent_widget)
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()
            
        except Exception as e:
            logger.error(f"Error showing warning dialog: {e}")


def error_handler(context: str = "", show_dialog: bool = True, reraise: bool = False):
    """
    Decorator for automatic error handling.
    
    Args:
        context: Context description for the error
        show_dialog: Whether to show error dialog
        reraise: Whether to reraise the exception after handling
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Try to find an error handler in the instance
                error_handler_instance = None
                if args and hasattr(args[0], '_error_handler'):
                    error_handler_instance = args[0]._error_handler
                elif args and hasattr(args[0], 'error_handler'):
                    error_handler_instance = args[0].error_handler
                
                if error_handler_instance:
                    error_handler_instance.handle_error(e, context or func.__name__, show_dialog)
                else:
                    # Fallback to logging
                    logger.error(f"Error in {context or func.__name__}: {e}", exc_info=True)
                
                if reraise:
                    raise
                
        return wrapper
    return decorator


def safe_execute(func: Callable, *args, default_return=None, context: str = "", **kwargs) -> Any:
    """
    Safely execute a function with error handling.
    
    Args:
        func: Function to execute
        *args: Function arguments
        default_return: Value to return on error
        context: Context for error logging
        **kwargs: Function keyword arguments
        
    Returns:
        Function result or default_return on error
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error in {context or func.__name__}: {e}", exc_info=True)
        return default_return
