"""
Custom exceptions for MultiCamCollector services.

This module defines custom exception classes for better
error handling and debugging throughout the application.
"""

from typing import Optional, Any, Dict


class MultiCamError(Exception):
    """Base exception class for MultiCamCollector errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize the exception.
        
        Args:
            message: Error message
            details: Optional dictionary with additional error details
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self) -> str:
        """Return string representation of the error."""
        if self.details:
            return f"{self.message} (Details: {self.details})"
        return self.message


class DeviceError(MultiCamError):
    """Exception raised for device-related errors."""
    
    def __init__(self, message: str, device_id: Optional[str] = None, **kwargs):
        """
        Initialize the device error.
        
        Args:
            message: Error message
            device_id: ID of the device that caused the error
            **kwargs: Additional error details
        """
        details = kwargs
        if device_id:
            details['device_id'] = device_id
        super().__init__(message, details)


class CameraError(DeviceError):
    """Exception raised for camera-specific errors."""
    pass


class CaptureError(MultiCamError):
    """Exception raised for capture-related errors."""
    
    def __init__(self, message: str, camera_id: Optional[str] = None, **kwargs):
        """
        Initialize the capture error.
        
        Args:
            message: Error message
            camera_id: ID of the camera that caused the error
            **kwargs: Additional error details
        """
        details = kwargs
        if camera_id:
            details['camera_id'] = camera_id
        super().__init__(message, details)


class StorageError(MultiCamError):
    """Exception raised for storage-related errors."""
    
    def __init__(self, message: str, path: Optional[str] = None, **kwargs):
        """
        Initialize the storage error.
        
        Args:
            message: Error message
            path: Storage path that caused the error
            **kwargs: Additional error details
        """
        details = kwargs
        if path:
            details['path'] = path
        super().__init__(message, details)


class ConfigurationError(MultiCamError):
    """Exception raised for configuration-related errors."""
    
    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        """
        Initialize the configuration error.
        
        Args:
            message: Error message
            config_key: Configuration key that caused the error
            **kwargs: Additional error details
        """
        details = kwargs
        if config_key:
            details['config_key'] = config_key
        super().__init__(message, details)


class ValidationError(MultiCamError):
    """Exception raised for validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None, **kwargs):
        """
        Initialize the validation error.
        
        Args:
            message: Error message
            field: Field name that failed validation
            value: Value that failed validation
            **kwargs: Additional error details
        """
        details = kwargs
        if field:
            details['field'] = field
        if value is not None:
            details['value'] = value
        super().__init__(message, details)


class SynchronizationError(CaptureError):
    """Exception raised for frame synchronization errors."""
    
    def __init__(self, message: str, max_jitter: Optional[float] = None, **kwargs):
        """
        Initialize the synchronization error.
        
        Args:
            message: Error message
            max_jitter: Maximum jitter detected
            **kwargs: Additional error details
        """
        details = kwargs
        if max_jitter is not None:
            details['max_jitter'] = max_jitter
        super().__init__(message, **details)
