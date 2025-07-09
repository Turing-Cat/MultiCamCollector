"""
Main application class for MultiCamCollector.

This module contains the core application logic and lifecycle management,
providing a clean separation between the Qt application and business logic.
"""

import os
from pathlib import Path
from typing import Optional

from src.config import load_config, get_config, ApplicationConfig
from src.utils.logging_config import get_logger
from src.container import setup_services, get_container
from src.controllers.main_window_controller import MainWindowController

logger = get_logger(__name__)


class MultiCamApplication:
    """
    Main application class that manages the lifecycle of the MultiCamCollector.
    
    This class handles:
    - Configuration loading
    - Service initialization
    - Main window creation and management
    - Application cleanup
    """
    
    def __init__(self):
        self._config: Optional[ApplicationConfig] = None
        self._main_controller: Optional[MainWindowController] = None
        self._project_root: str = str(Path(__file__).parent.parent.absolute())
        self._initialized: bool = False
    
    def initialize(self) -> None:
        """
        Initialize the application.
        
        This method loads configuration, sets up services, and prepares
        the application for use.
        
        Raises:
            RuntimeError: If initialization fails
        """
        if self._initialized:
            logger.warning("Application already initialized")
            return
        
        try:
            logger.info("Initializing MultiCamCollector application...")
            
            # Load configuration
            config_path = os.path.join(self._project_root, "config.yaml")
            self._config = load_config(config_path)
            logger.info("Configuration loaded successfully")

            # Setup dependency injection container
            setup_services()
            logger.info("Services container initialized")

            # Initialize main window controller
            self._main_controller = MainWindowController(self._project_root)
            logger.info("Main window controller initialized")
            
            self._initialized = True
            logger.info("Application initialization completed")
            
        except Exception as e:
            logger.error(f"Failed to initialize application: {e}", exc_info=True)
            raise RuntimeError(f"Application initialization failed: {e}") from e
    
    def show(self) -> None:
        """
        Show the main application window.
        
        Raises:
            RuntimeError: If application is not initialized
        """
        if not self._initialized:
            raise RuntimeError("Application not initialized. Call initialize() first.")
        
        if self._main_controller is None:
            raise RuntimeError("Main controller not available")
        
        logger.info("Showing main application window")
        self._main_controller.show()
    
    def cleanup(self) -> None:
        """
        Clean up application resources.
        
        This method should be called before application exit to ensure
        proper cleanup of resources.
        """
        if not self._initialized:
            return
        
        logger.info("Cleaning up application resources...")
        
        try:
            # Cleanup main controller if it exists
            if self._main_controller:
                # The controller cleanup will be handled by Qt's close event
                pass
            
            logger.info("Application cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during application cleanup: {e}", exc_info=True)
        finally:
            self._initialized = False
    
    @property
    def config(self) -> ApplicationConfig:
        """
        Get the application configuration.
        
        Returns:
            ApplicationConfig instance
            
        Raises:
            RuntimeError: If application is not initialized
        """
        if not self._initialized:
            raise RuntimeError("Application not initialized")
        return get_config()
    
    @property
    def project_root(self) -> str:
        """Get the project root directory."""
        return self._project_root
    
    @property
    def is_initialized(self) -> bool:
        """Check if the application is initialized."""
        return self._initialized
