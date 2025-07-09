# Development Guide

This guide provides detailed information for developers working on the MultiCamCollector project.

## Architecture Overview

### Core Principles

1. **Layered Architecture**: Clear separation between GUI, business logic, and hardware abstraction
2. **Dependency Injection**: Services are injected rather than instantiated directly
3. **Interface-Based Design**: All services implement well-defined interfaces
4. **Error Handling**: Comprehensive error handling with custom exceptions
5. **Configuration Management**: Centralized, type-safe configuration

### Layer Responsibilities

#### Core Layer (`core/`)
- **Application Lifecycle**: Main application initialization and cleanup
- **Configuration**: Centralized configuration management with validation
- **Dependency Injection**: Service container and dependency resolution
- **Error Handling**: Centralized error handling and user notifications
- **Logging**: Structured logging configuration
- **Validation**: Input validation utilities

#### GUI Layer (`gui/`)
- **Base Classes**: Common widget functionality and patterns
- **Widget Factory**: Dependency injection for GUI components
- **Widgets**: Specific UI components (panels, previews, etc.)
- **No Business Logic**: GUI components should only handle presentation

#### Main Window (`main_window/`)
- **Controller**: Coordinates between GUI and services (MVC pattern)
- **View**: Main window layout and widget composition

#### Services Layer (`services/`)
- **Interfaces**: Abstract base classes defining service contracts
- **Business Logic**: Core application functionality
- **Device Management**: Camera discovery and lifecycle management
- **Data Storage**: File system operations and data organization
- **Configuration Access**: Service-level configuration access

#### Device Layer (`devices/`)
- **Hardware Abstraction**: Common interface for different camera types
- **Device Implementations**: Specific camera implementations
- **Mock Devices**: Testing and development support

#### Models (`models/`)
- **Data Structures**: Application data models and DTOs
- **Validation**: Model-level validation logic

## Development Workflow

### Setting Up Development Environment

1. **Clone and Setup**:
```bash
git clone <repository-url>
cd MultiCamCollector
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

2. **IDE Configuration**:
   - Configure your IDE for Python 3.9+
   - Enable type checking (mypy)
   - Set up code formatting (black, isort)
   - Configure linting (flake8, pylint)

3. **Pre-commit Hooks**:
```bash
pre-commit install
```

### Code Standards

#### Type Hints
All functions must have complete type annotations:

```python
def process_frame(frame: Frame, settings: Dict[str, Any]) -> Optional[ProcessedFrame]:
    """Process a camera frame with given settings."""
    pass
```

#### Docstrings
Use Google-style docstrings for all public methods:

```python
def capture_frames(self, camera_ids: List[str]) -> List[Frame]:
    """
    Capture frames from specified cameras.
    
    Args:
        camera_ids: List of camera IDs to capture from
        
    Returns:
        List of captured frames
        
    Raises:
        CaptureError: If capture fails for any camera
    """
    pass
```

#### Error Handling
Use custom exceptions and proper error handling:

```python
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise ServiceError(f"Failed to complete operation: {e}") from e
```

#### Logging
Use structured logging with appropriate levels:

```python
logger = get_logger(__name__)

logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning about potential issues")
logger.error("Error that needs attention", exc_info=True)
```

### Adding New Features

#### 1. Adding a New Service

1. **Define Interface**:
```python
# services/interfaces/my_service_interface.py
from abc import ABC, abstractmethod

class IMyService(ABC):
    @abstractmethod
    def do_something(self, param: str) -> bool:
        pass
```

2. **Implement Service**:
```python
# services/my_service.py
from services.interfaces.my_service_interface import IMyService

class MyService(IMyService):
    def do_something(self, param: str) -> bool:
        # Implementation
        pass
```

3. **Register in Container**:
```python
# core/container.py
def setup_services():
    # ... existing registrations
    container.register_factory(MyService, lambda: MyService())
```

#### 2. Adding a New Widget

1. **Create Widget Class**:
```python
# gui/widgets/my_widget.py
from gui.base import BaseWidget

class MyWidget(BaseWidget):
    def _setup_widget(self) -> None:
        # Widget-specific setup
        pass
    
    def _connect_signals(self) -> None:
        # Signal connections
        pass
```

2. **Add to Factory**:
```python
# gui/base/widget_factory.py
def create_my_widget(self, **kwargs) -> 'MyWidget':
    from gui.widgets.my_widget import MyWidget
    return self.create_widget(MyWidget, **kwargs)
```

#### 3. Adding a New Camera Type

1. **Implement Camera Class**:
```python
# devices/my_camera.py
from devices.abstract_camera import AbstractCamera

class MyCamera(AbstractCamera):
    def connect(self) -> bool:
        # Implementation
        pass
    
    def capture_frame(self) -> Optional[Frame]:
        # Implementation
        pass
```

2. **Update Device Manager**:
```python
# services/device_manager.py
def _discover_my_cameras(self) -> int:
    # Discovery logic
    pass

def discover_cameras(self) -> List[AbstractCamera]:
    # Add call to _discover_my_cameras
    pass
```

### Testing

#### Unit Tests
Write unit tests for all new functionality:

```python
# tests/test_my_service.py
import pytest
from services.my_service import MyService

class TestMyService:
    def test_do_something_success(self):
        service = MyService()
        result = service.do_something("test")
        assert result is True
    
    def test_do_something_failure(self):
        service = MyService()
        with pytest.raises(ServiceError):
            service.do_something("invalid")
```

#### Integration Tests
Test component interactions:

```python
# tests/integration/test_capture_flow.py
def test_full_capture_flow(mock_cameras):
    # Test complete capture workflow
    pass
```

#### GUI Tests
Use pytest-qt for GUI testing:

```python
# tests/gui/test_metadata_panel.py
def test_metadata_panel_validation(qtbot):
    panel = MetadataPanel(".")
    qtbot.addWidget(panel)
    # Test validation logic
```

### Debugging

#### Logging Configuration
Adjust logging levels for debugging:

```python
# In development, use DEBUG level
setup_logging(log_level="DEBUG")
```

#### Mock Cameras
Use mock cameras for development without hardware:

```python
# The application automatically falls back to mock cameras
# when no real cameras are detected
```

#### Error Handling
Use the error handler for debugging:

```python
from core.error_handler import ErrorHandler

error_handler = ErrorHandler()
error_handler.handle_error(exception, "context", show_dialog=False)
```

### Performance Considerations

#### Camera Threading
- Each camera runs in its own thread
- Use thread-safe operations for shared data
- Minimize blocking operations in the main thread

#### Memory Management
- Properly dispose of camera resources
- Use context managers where appropriate
- Monitor memory usage with large datasets

#### GUI Responsiveness
- Keep heavy operations off the main thread
- Use signals for thread communication
- Implement progress indicators for long operations

### Common Patterns

#### Service Access
```python
from core.container import get_container

container = get_container()
storage_service = container.get(StorageService)
```

#### Error Handling Decorator
```python
from core.error_handler import error_handler

@error_handler("operation context")
def risky_operation(self):
    # Implementation
    pass
```

#### Validation
```python
from core.validation import Validator, validate_and_raise

validation_result = Validator.validate_path(path)
validate_and_raise(validation_result, "storage path")
```

### Release Process

1. **Version Bump**: Update version in `__init__.py`
2. **Changelog**: Update `CHANGELOG.md`
3. **Tests**: Ensure all tests pass
4. **Documentation**: Update documentation
5. **Build**: Create distribution packages
6. **Tag**: Create git tag for release

### Troubleshooting Development Issues

#### Import Errors
- Check Python path configuration
- Verify virtual environment activation
- Ensure all dependencies are installed

#### Camera Issues
- Verify SDK installations
- Check device permissions
- Use mock cameras for development

#### GUI Issues
- Check Qt installation
- Verify UI file paths
- Use Qt Designer for UI modifications

## Best Practices

1. **Keep It Simple**: Prefer simple, readable code over clever solutions
2. **Test Early**: Write tests as you develop features
3. **Document Everything**: Code should be self-documenting with good names and comments
4. **Handle Errors**: Always consider what can go wrong and handle it gracefully
5. **Use Type Hints**: They improve code quality and IDE support
6. **Follow Patterns**: Use established patterns consistently throughout the codebase
