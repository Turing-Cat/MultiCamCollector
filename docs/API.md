# API Documentation

This document provides detailed API documentation for the MultiCamCollector application.

## Core APIs

### Application (`core.application`)

#### MultiCamApplication

Main application class that manages the lifecycle of the MultiCamCollector.

```python
class MultiCamApplication:
    def __init__(self) -> None
    def initialize(self) -> None
    def show(self) -> None
    def cleanup(self) -> None
    
    @property
    def config(self) -> ApplicationConfig
    @property
    def project_root(self) -> str
    @property
    def is_initialized(self) -> bool
```

**Methods:**
- `initialize()`: Initialize the application with configuration and services
- `show()`: Show the main application window
- `cleanup()`: Clean up application resources

### Configuration (`core.config`)

#### ApplicationConfig

Main configuration class with type-safe access to settings.

```python
@dataclass
class ApplicationConfig:
    camera: CameraConfig
    zed: ZedConfig
    storage: StorageConfig
    logging: LoggingConfig
    
    @classmethod
    def load_from_file(cls, config_path: str) -> 'ApplicationConfig'
    def save_to_file(self, config_path: str) -> None
```

**Functions:**
- `get_config() -> ApplicationConfig`: Get the global configuration
- `load_config(config_path: str) -> ApplicationConfig`: Load configuration from file

### Dependency Injection (`core.container`)

#### ServiceContainer

Simple dependency injection container for managing services.

```python
class ServiceContainer:
    def register_singleton(self, service_type: Type[T], instance: T) -> None
    def register_factory(self, service_type: Type[T], factory: Callable[[], T]) -> None
    def get(self, service_type: Type[T]) -> T
    def has(self, service_type: Type[T]) -> bool
```

**Functions:**
- `get_container() -> ServiceContainer`: Get the global service container
- `setup_services() -> ServiceContainer`: Setup and configure all application services

### Error Handling (`core.error_handler`)

#### ErrorHandler

Centralized error handler for the application.

```python
class ErrorHandler(QObject):
    error_occurred = pyqtSignal(str, str)
    warning_occurred = pyqtSignal(str, str)
    
    def handle_error(self, error: Exception, context: str = "", show_dialog: bool = True) -> None
    def handle_warning(self, message: str, title: str = "Warning", show_dialog: bool = True) -> None
```

**Decorators:**
- `@error_handler(context: str, show_dialog: bool, reraise: bool)`: Automatic error handling decorator

### Validation (`core.validation`)

#### Validator

Utility class for common validation operations.

```python
class Validator:
    @staticmethod
    def validate_path(path: str, must_exist: bool = False, must_be_writable: bool = False) -> ValidationResult
    @staticmethod
    def validate_camera_id(camera_id: str) -> ValidationResult
    @staticmethod
    def validate_sequence_number(sequence_number: Union[int, str]) -> ValidationResult
    @staticmethod
    def validate_settings_dict(settings: Dict[str, Any]) -> ValidationResult
```

## Service APIs

### Device Management (`services.device_manager`)

#### IDeviceManager

Interface for device management services.

```python
class IDeviceManager(ABC):
    @abstractmethod
    def discover_cameras(self) -> List[AbstractCamera]
    @abstractmethod
    def get_all_cameras(self) -> List[AbstractCamera]
    @abstractmethod
    def get_camera_by_id(self, camera_id: str) -> Optional[AbstractCamera]
    @abstractmethod
    def get_connected_cameras(self) -> List[AbstractCamera]
    @abstractmethod
    def refresh_camera_status(self) -> None
    @abstractmethod
    def cleanup(self) -> None
```

### Storage (`services.storage_service`)

#### IStorageService

Interface for storage services.

```python
class IStorageService(ABC):
    @abstractmethod
    def save(self, frames: List[Frame], metadata: CaptureMetadata, settings: Dict[str, Any]) -> str
    @abstractmethod
    def set_root_dir(self, root_dir: str) -> None
    @abstractmethod
    def get_root_dir(self) -> str
    @abstractmethod
    def validate_storage_path(self, path: str) -> bool
    @abstractmethod
    def get_storage_info(self) -> Dict[str, Any]
```

### Capture Orchestration (`services.capture_orchestrator`)

#### ICaptureOrchestrator

Interface for capture orchestration services.

```python
class ICaptureOrchestrator(ABC):
    @abstractmethod
    def capture_all_frames(self) -> List[Frame]
    @abstractmethod
    def capture_single_frame(self, camera_id: str) -> Optional[Frame]
    @abstractmethod
    def get_capture_status(self) -> Dict[str, Any]
    @abstractmethod
    def validate_synchronization(self, frames: List[Frame]) -> bool
```

## Device APIs

### Abstract Camera (`devices.abstract_camera`)

#### AbstractCamera

Base class for all camera implementations.

```python
class AbstractCamera(ABC):
    @abstractmethod
    def connect(self) -> bool
    @abstractmethod
    def disconnect(self) -> None
    @abstractmethod
    def capture_frame(self) -> Optional[Frame]
    @abstractmethod
    def is_connected(self) -> bool
    @abstractmethod
    def get_camera_info(self) -> Dict[str, Any]
```

**Properties:**
- `camera_id: str`: Unique camera identifier
- `camera_type: str`: Camera type (e.g., "RealSense", "ZED")

## GUI APIs

### Base Widget (`gui.base.base_widget`)

#### BaseWidget

Base class for all custom widgets.

```python
class BaseWidget(QWidget, ABC):
    def __init__(self, project_root: str, ui_filename: Optional[str] = None)
    
    @abstractmethod
    def _setup_widget(self) -> None
    def _connect_signals(self) -> None
    
    @property
    def is_initialized(self) -> bool
    @property
    def project_root(self) -> str
```

### Widget Factory (`gui.base.widget_factory`)

#### WidgetFactory

Factory for creating GUI widgets with dependency injection.

```python
class WidgetFactory:
    def __init__(self, project_root: str)
    def create_widget(self, widget_class: Type[T], **kwargs: Any) -> T
    def create_preview_grid(self, device_manager) -> 'PreviewGrid'
    def create_metadata_panel(self) -> 'MetadataPanel'
    def create_log_panel(self) -> 'LogPanel'
    def create_settings_panel(self, default_path: str) -> 'SettingsPanel'
```

### Metadata Panel (`gui.widgets.metadata_panel`)

#### MetadataPanel

Widget for configuring capture metadata.

```python
class MetadataPanel(BaseWidget):
    capture_requested = pyqtSignal()
    metadata_changed = pyqtSignal(CaptureMetadata)
    
    def get_metadata(self) -> CaptureMetadata
    def set_metadata(self, metadata: CaptureMetadata) -> None
    def is_locked(self) -> bool
    def set_locked(self, locked: bool) -> None
```

### Settings Panel (`gui.widgets.settings_panel`)

#### SettingsPanel

Widget for configuring data saving settings.

```python
class SettingsPanel(BaseWidget):
    settings_changed = pyqtSignal(dict)
    path_changed = pyqtSignal(str)
    
    def get_settings(self) -> Dict[str, Any]
    def set_settings(self, settings: Dict[str, Any]) -> None
    def validate_path(self, path: str) -> bool
```

### Log Panel (`gui.widgets.log_panel`)

#### LogPanel

Widget for displaying log messages.

```python
class LogPanel(BaseWidget):
    def add_log_message(self, message: str, level: str = "INFO") -> None
    def add_info_message(self, message: str) -> None
    def add_warning_message(self, message: str) -> None
    def add_error_message(self, message: str) -> None
    def clear_messages(self) -> None
    
    @property
    def message_count(self) -> int
```

### Preview Grid (`gui.widgets.preview_widget`)

#### PreviewGrid

Grid of preview widgets for camera feeds.

```python
class PreviewGrid(QWidget):
    def __init__(self, project_root: str, device_manager)
    def get_last_frames(self) -> List[Frame]
    def stop_threads(self) -> None
```

## Model APIs

### Camera Models (`models.camera`)

#### Frame

Represents a captured frame from a camera.

```python
@dataclass
class Frame:
    camera_id: str
    timestamp: datetime
    rgb_image: Optional[np.ndarray]
    depth_image: Optional[np.ndarray]
    camera_info: Dict[str, Any]
```

### Metadata Models (`models.metadata`)

#### CaptureMetadata

Represents metadata for a capture session.

```python
@dataclass
class CaptureMetadata:
    lighting: LightingLevel
    background_id: str
    sequence_number: int
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CaptureMetadata'
```

#### LightingLevel

Enumeration of lighting conditions.

```python
class LightingLevel(Enum):
    BRIGHT = "bright"
    NORMAL = "normal"
    DIM = "dim"
    DARK = "dark"
```

## Exception APIs

### Custom Exceptions (`services.exceptions`)

#### Exception Hierarchy

```python
MultiCamError(Exception)
├── DeviceError(MultiCamError)
│   └── CameraError(DeviceError)
├── CaptureError(MultiCamError)
│   └── SynchronizationError(CaptureError)
├── StorageError(MultiCamError)
├── ConfigurationError(MultiCamError)
└── ValidationError(MultiCamError)
```

**Common Properties:**
- `message: str`: Error message
- `details: Dict[str, Any]`: Additional error details

## Usage Examples

### Basic Application Setup

```python
from core.application import MultiCamApplication
from core.logging_config import setup_logging

# Setup logging
setup_logging()

# Create and run application
app = MultiCamApplication()
app.initialize()
app.show()
```

### Service Access

```python
from core.container import get_container
from services.storage_service import StorageService

container = get_container()
storage_service = container.get(StorageService)
```

### Error Handling

```python
from core.error_handler import error_handler, ErrorHandler

@error_handler("capture operation")
def capture_frames(self):
    # Implementation that may raise exceptions
    pass

# Or manual error handling
error_handler = ErrorHandler()
try:
    risky_operation()
except Exception as e:
    error_handler.handle_error(e, "operation context")
```

### Validation

```python
from core.validation import Validator, validate_and_raise

# Validate and get result
result = Validator.validate_path("/some/path", must_be_writable=True)
if not result:
    print(f"Validation errors: {result.errors}")

# Validate and raise on error
validate_and_raise(result, "storage path")
```
