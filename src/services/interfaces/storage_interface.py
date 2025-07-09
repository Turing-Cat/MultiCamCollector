"""
Storage service interface.

This module defines the interface for storage services
to enable dependency injection and testing.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pathlib import Path

from models.camera import Frame
from models.metadata import CaptureMetadata


class IStorageService(ABC):
    """
    Interface for storage services.
    
    This interface defines the contract for saving captured frames
    and metadata to persistent storage.
    """
    
    @abstractmethod
    def save(
        self, 
        frames: List[Frame], 
        metadata: CaptureMetadata, 
        settings: Dict[str, Any]
    ) -> str:
        """
        Save frames and metadata to storage.
        
        Args:
            frames: List of frames to save
            metadata: Capture metadata
            settings: Storage settings
            
        Returns:
            Path to the saved session directory
            
        Raises:
            StorageError: If saving fails
        """
        pass
    
    @abstractmethod
    def set_root_dir(self, root_dir: str) -> None:
        """
        Set the root directory for storage.
        
        Args:
            root_dir: Path to the root storage directory
            
        Raises:
            StorageError: If directory is invalid or inaccessible
        """
        pass
    
    @abstractmethod
    def get_root_dir(self) -> str:
        """
        Get the current root storage directory.
        
        Returns:
            Path to the root storage directory
        """
        pass
    
    @abstractmethod
    def validate_storage_path(self, path: str) -> bool:
        """
        Validate a storage path.
        
        Args:
            path: Path to validate
            
        Returns:
            True if path is valid and accessible
        """
        pass
    
    @abstractmethod
    def get_storage_info(self) -> Dict[str, Any]:
        """
        Get information about the storage system.
        
        Returns:
            Dictionary containing storage information (free space, etc.)
        """
        pass
