"""
Dependency injection container for MultiCamCollector.

This module provides a simple dependency injection container to manage
service dependencies and improve testability.
"""

from typing import Dict, Any, TypeVar, Type, Optional, Callable
import platform
import os

from src.config import get_config, ApplicationConfig
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


class ServiceContainer:
    """
    Simple dependency injection container for managing services.
    
    This container provides:
    - Service registration and resolution
    - Singleton pattern for services
    - Lazy initialization
    - Type-safe service access
    """
    
    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable[[], Any]] = {}
        self._singletons: Dict[Type, Any] = {}
    
    def register_singleton(self, service_type: Type[T], instance: T) -> None:
        """
        Register a singleton service instance.
        
        Args:
            service_type: The service type/interface
            instance: The service instance
        """
        self._singletons[service_type] = instance
        logger.debug(f"Registered singleton service: {service_type.__name__}")
    
    def register_factory(self, service_type: Type[T], factory: Callable[[], T]) -> None:
        """
        Register a factory function for creating service instances.
        
        Args:
            service_type: The service type/interface
            factory: Factory function that creates the service
        """
        self._factories[service_type] = factory
        logger.debug(f"Registered factory for service: {service_type.__name__}")
    
    def get(self, service_type: Type[T]) -> T:
        """
        Get a service instance.
        
        Args:
            service_type: The service type to retrieve
            
        Returns:
            Service instance
            
        Raises:
            ValueError: If service is not registered
        """
        # Check singletons first
        if service_type in self._singletons:
            return self._singletons[service_type]
        
        # Check if we have a factory
        if service_type in self._factories:
            instance = self._factories[service_type]()
            # Store as singleton for future requests
            self._singletons[service_type] = instance
            return instance
        
        raise ValueError(f"Service {service_type.__name__} is not registered")
    
    def has(self, service_type: Type[T]) -> bool:
        """
        Check if a service is registered.
        
        Args:
            service_type: The service type to check
            
        Returns:
            True if service is registered
        """
        return (service_type in self._singletons or 
                service_type in self._factories)
    
    def clear(self) -> None:
        """Clear all registered services."""
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()
        logger.debug("Service container cleared")


# Global container instance
_container: Optional[ServiceContainer] = None


def get_container() -> ServiceContainer:
    """
    Get the global service container.
    
    Returns:
        ServiceContainer instance
    """
    global _container
    if _container is None:
        _container = ServiceContainer()
    return _container


def setup_services() -> ServiceContainer:
    """
    Setup and configure all application services.
    
    This function registers all the core services with the container
    using the current configuration.
    
    Returns:
        Configured ServiceContainer
    """
    container = get_container()
    config = get_config()
    
    logger.info("Setting up application services...")
    
    # Register configuration service
    from src.services.config_service import ConfigService
    container.register_factory(ConfigService, lambda: ConfigService())
    
    # Register device manager
    from src.services.device_manager import DeviceManager
    def create_device_manager():
        zed_sdk_path = _get_zed_sdk_path()
        return DeviceManager(zed_sdk_path=zed_sdk_path)
    container.register_factory(DeviceManager, create_device_manager)
    
    # Register storage service
    from src.services.storage_service import StorageService
    def create_storage_service():
        storage_path = _resolve_storage_path(config)
        return StorageService(root_dir=storage_path)
    container.register_factory(StorageService, create_storage_service)
    
    # Register sequence counter
    from src.services.sequence_counter import SequenceCounter
    def create_sequence_counter():
        storage_path = _resolve_storage_path(config)
        return SequenceCounter(storage_dir=storage_path)
    container.register_factory(SequenceCounter, create_sequence_counter)
    
    logger.info("Application services setup completed")
    return container


def _get_zed_sdk_path() -> Optional[str]:
    """Get ZED SDK installation path based on the platform."""
    if platform.system() == "Windows":
        return os.environ.get("ZED_SDK_ROOT_DIR", "C:/Program Files (x86)/ZED SDK")
    if platform.system() == "Linux":
        return os.environ.get("ZED_SDK_ROOT_DIR", "/usr/local/zed")
    return None


def _resolve_storage_path(config: ApplicationConfig) -> str:
    """Resolve the storage path from configuration."""
    storage_path = config.storage.dataset_root_dir
    
    # Handle relative paths
    if not os.path.isabs(storage_path):
        # Get the project root (parent of core directory)
        project_root = os.path.dirname(os.path.dirname(__file__))
        storage_path = os.path.join(
            os.path.dirname(project_root), 
            storage_path.lstrip('./')
        )
    
    # Ensure the directory exists
    os.makedirs(storage_path, exist_ok=True)
    return storage_path
