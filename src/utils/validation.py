"""
Validation utilities for MultiCamCollector.

This module provides validation functions for various data types
and application-specific validation logic.
"""

import re
from pathlib import Path
from typing import Any, List, Dict, Optional, Union
from dataclasses import dataclass

from src.services.exceptions import ValidationError
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class ValidationResult:
    """Result of a validation operation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    
    def __bool__(self) -> bool:
        """Return True if validation passed."""
        return self.is_valid
    
    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        self.warnings.append(warning)


class Validator:
    """
    Utility class for common validation operations.
    
    This class provides static methods for validating various
    types of data commonly used in the application.
    """
    
    @staticmethod
    def validate_path(path: str, must_exist: bool = False, must_be_writable: bool = False) -> ValidationResult:
        """
        Validate a file system path.
        
        Args:
            path: Path to validate
            must_exist: Whether the path must already exist
            must_be_writable: Whether the path must be writable
            
        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult(True, [], [])
        
        if not path or not path.strip():
            result.add_error("Path cannot be empty")
            return result
        
        try:
            path_obj = Path(path)
            
            if must_exist and not path_obj.exists():
                result.add_error(f"Path does not exist: {path}")
            
            if must_be_writable:
                if path_obj.exists():
                    if not path_obj.is_dir():
                        result.add_error(f"Path is not a directory: {path}")
                    elif not path_obj.stat().st_mode & 0o200:  # Check write permission
                        result.add_error(f"Path is not writable: {path}")
                else:
                    # Try to create parent directories to test writability
                    try:
                        path_obj.mkdir(parents=True, exist_ok=True)
                        if not path_obj.exists():
                            result.add_error(f"Cannot create directory: {path}")
                    except PermissionError:
                        result.add_error(f"No permission to create directory: {path}")
                    except Exception as e:
                        result.add_error(f"Error validating path: {e}")
            
        except Exception as e:
            result.add_error(f"Invalid path format: {e}")
        
        return result
    
    @staticmethod
    def validate_camera_id(camera_id: str) -> ValidationResult:
        """
        Validate a camera ID.
        
        Args:
            camera_id: Camera ID to validate
            
        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult(True, [], [])
        
        if not camera_id or not camera_id.strip():
            result.add_error("Camera ID cannot be empty")
            return result
        
        # Check format (letters, numbers, underscores, hyphens)
        if not re.match(r'^[a-zA-Z0-9_-]+$', camera_id):
            result.add_error("Camera ID can only contain letters, numbers, underscores, and hyphens")
        
        # Check length
        if len(camera_id) > 50:
            result.add_error("Camera ID cannot be longer than 50 characters")
        
        return result
    
    @staticmethod
    def validate_sequence_number(sequence_number: Union[int, str]) -> ValidationResult:
        """
        Validate a sequence number.
        
        Args:
            sequence_number: Sequence number to validate
            
        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult(True, [], [])
        
        try:
            seq_num = int(sequence_number)
            
            if seq_num < 1:
                result.add_error("Sequence number must be positive")
            elif seq_num > 999999:
                result.add_error("Sequence number cannot exceed 999999")
                
        except (ValueError, TypeError):
            result.add_error("Sequence number must be a valid integer")
        
        return result
    
    @staticmethod
    def validate_background_id(background_id: str) -> ValidationResult:
        """
        Validate a background ID.
        
        Args:
            background_id: Background ID to validate
            
        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult(True, [], [])
        
        if not background_id or not background_id.strip():
            result.add_error("Background ID cannot be empty")
            return result
        
        # Check format (letters, numbers, underscores, hyphens)
        if not re.match(r'^[a-zA-Z0-9_-]+$', background_id):
            result.add_error("Background ID can only contain letters, numbers, underscores, and hyphens")
        
        # Check length
        if len(background_id) > 100:
            result.add_error("Background ID cannot be longer than 100 characters")
        
        return result
    
    @staticmethod
    def validate_resolution(resolution: str) -> ValidationResult:
        """
        Validate a camera resolution string.
        
        Args:
            resolution: Resolution string (e.g., "1920x1080")
            
        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult(True, [], [])
        
        if not resolution or not resolution.strip():
            result.add_error("Resolution cannot be empty")
            return result
        
        # Check format
        if not re.match(r'^\d+x\d+$', resolution):
            result.add_error("Resolution must be in format 'WIDTHxHEIGHT' (e.g., '1920x1080')")
            return result
        
        try:
            width, height = map(int, resolution.split('x'))
            
            if width < 1 or height < 1:
                result.add_error("Resolution dimensions must be positive")
            elif width > 7680 or height > 4320:  # 8K limit
                result.add_warning("Very high resolution may impact performance")
                
        except ValueError:
            result.add_error("Invalid resolution format")
        
        return result
    
    @staticmethod
    def validate_fps(fps: Union[int, str]) -> ValidationResult:
        """
        Validate frames per second value.
        
        Args:
            fps: FPS value to validate
            
        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult(True, [], [])
        
        try:
            fps_value = int(fps)
            
            if fps_value < 1:
                result.add_error("FPS must be positive")
            elif fps_value > 120:
                result.add_warning("Very high FPS may impact performance")
                
        except (ValueError, TypeError):
            result.add_error("FPS must be a valid integer")
        
        return result
    
    @staticmethod
    def validate_settings_dict(settings: Dict[str, Any]) -> ValidationResult:
        """
        Validate a settings dictionary.
        
        Args:
            settings: Settings dictionary to validate
            
        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult(True, [], [])
        
        if not isinstance(settings, dict):
            result.add_error("Settings must be a dictionary")
            return result
        
        # Check for required keys
        required_keys = ['save_rgb', 'save_depth', 'save_point_cloud', 'path']
        for key in required_keys:
            if key not in settings:
                result.add_error(f"Missing required setting: {key}")
        
        # Validate path if present
        if 'path' in settings:
            path_result = Validator.validate_path(settings['path'], must_be_writable=True)
            if not path_result:
                result.errors.extend(path_result.errors)
                result.warnings.extend(path_result.warnings)
                result.is_valid = False
        
        # Validate boolean settings
        bool_settings = ['save_rgb', 'save_depth', 'save_point_cloud']
        for key in bool_settings:
            if key in settings and not isinstance(settings[key], bool):
                result.add_error(f"Setting '{key}' must be a boolean")
        
        return result


def validate_and_raise(validation_result: ValidationResult, context: str = "") -> None:
    """
    Raise ValidationError if validation failed.
    
    Args:
        validation_result: Result of validation
        context: Additional context for the error
        
    Raises:
        ValidationError: If validation failed
    """
    if not validation_result.is_valid:
        error_msg = f"Validation failed{' for ' + context if context else ''}"
        details = {
            'errors': validation_result.errors,
            'warnings': validation_result.warnings
        }
        raise ValidationError(error_msg, **details)
