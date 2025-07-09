"""
Service interfaces for MultiCamCollector.

This package contains abstract base classes and interfaces
for all services to improve testability and maintainability.
"""

from .storage_interface import IStorageService
from .device_interface import IDeviceManager
from .capture_interface import ICaptureOrchestrator

__all__ = [
    'IStorageService',
    'IDeviceManager', 
    'ICaptureOrchestrator'
]
