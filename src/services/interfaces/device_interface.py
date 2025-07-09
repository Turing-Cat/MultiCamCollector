"""
Device manager interface.

This module defines the interface for device management services
to enable dependency injection and testing.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from devices.abstract_camera import AbstractCamera


class IDeviceManager(ABC):
    """
    Interface for device management services.
    
    This interface defines the contract for discovering,
    managing, and monitoring camera devices.
    """
    
    @abstractmethod
    def discover_cameras(self) -> List[AbstractCamera]:
        """
        Discover and initialize available cameras.
        
        Returns:
            List of discovered camera instances
            
        Raises:
            DeviceError: If discovery fails
        """
        pass
    
    @abstractmethod
    def get_all_cameras(self) -> List[AbstractCamera]:
        """
        Get all currently managed cameras.
        
        Returns:
            List of all camera instances
        """
        pass
    
    @abstractmethod
    def get_camera_by_id(self, camera_id: str) -> Optional[AbstractCamera]:
        """
        Get a camera by its ID.
        
        Args:
            camera_id: ID of the camera to retrieve
            
        Returns:
            Camera instance or None if not found
        """
        pass
    
    @abstractmethod
    def get_connected_cameras(self) -> List[AbstractCamera]:
        """
        Get all currently connected cameras.
        
        Returns:
            List of connected camera instances
        """
        pass
    
    @abstractmethod
    def refresh_camera_status(self) -> None:
        """
        Refresh the connection status of all cameras.
        
        Raises:
            DeviceError: If status refresh fails
        """
        pass
    
    @abstractmethod
    def get_device_info(self) -> Dict[str, Any]:
        """
        Get information about managed devices.
        
        Returns:
            Dictionary containing device information
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """
        Clean up device resources.
        
        This method should be called before shutdown to properly
        release device resources.
        """
        pass
