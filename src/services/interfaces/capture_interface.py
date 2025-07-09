"""
Capture orchestrator interface.

This module defines the interface for capture orchestration services
to enable dependency injection and testing.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from models.camera import Frame


class ICaptureOrchestrator(ABC):
    """
    Interface for capture orchestration services.
    
    This interface defines the contract for coordinating
    frame capture across multiple cameras.
    """
    
    @abstractmethod
    def capture_all_frames(self) -> List[Frame]:
        """
        Capture frames from all available cameras.
        
        Returns:
            List of captured frames from all cameras
            
        Raises:
            CaptureError: If capture fails
        """
        pass
    
    @abstractmethod
    def capture_single_frame(self, camera_id: str) -> Optional[Frame]:
        """
        Capture a frame from a specific camera.
        
        Args:
            camera_id: ID of the camera to capture from
            
        Returns:
            Captured frame or None if capture fails
            
        Raises:
            CaptureError: If capture fails
        """
        pass
    
    @abstractmethod
    def get_capture_status(self) -> Dict[str, Any]:
        """
        Get the current capture status.
        
        Returns:
            Dictionary containing capture status information
        """
        pass
    
    @abstractmethod
    def validate_synchronization(self, frames: List[Frame]) -> bool:
        """
        Validate that frames are properly synchronized.
        
        Args:
            frames: List of frames to validate
            
        Returns:
            True if frames are synchronized within acceptable limits
        """
        pass
    
    @abstractmethod
    def get_synchronization_info(self, frames: List[Frame]) -> Dict[str, Any]:
        """
        Get synchronization information for a set of frames.
        
        Args:
            frames: List of frames to analyze
            
        Returns:
            Dictionary containing synchronization metrics
        """
        pass
