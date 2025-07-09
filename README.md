# MultiCamCollector

A professional multi-camera data collection application for synchronized RGB-D capture from Intel RealSense and ZED cameras.

## Features

- **Multi-Camera Support**: Simultaneous capture from multiple Intel RealSense D435i and ZED 2i cameras
- **Synchronized Capture**: Software-based frame synchronization across all connected cameras
- **Real-time Preview**: Live preview of all camera feeds with automatic layout
- **Flexible Storage**: Configurable data formats (RGB, Depth, Point Cloud) with organized directory structure
- **Robust Architecture**: Clean separation of concerns with dependency injection and comprehensive error handling
- **User-Friendly Interface**: Intuitive Qt-based GUI with real-time logging and status monitoring

## Architecture

The application follows a layered architecture with clear separation of concerns:

```
MultiCamCollector/
├── core/                   # Core application infrastructure
│   ├── application.py      # Main application lifecycle management
│   ├── config.py          # Centralized configuration management
│   ├── container.py       # Dependency injection container
│   ├── error_handler.py   # Error handling utilities
│   ├── logging_config.py  # Logging configuration
│   └── validation.py      # Input validation utilities
├── gui/                   # User interface components
│   ├── base/              # Base classes and factories
│   │   ├── base_widget.py # Base widget class
│   │   └── widget_factory.py # Widget factory for DI
│   └── widgets/           # Specific widget implementations
│       ├── log_panel.py   # Log display widget
│       ├── metadata_panel.py # Metadata configuration
│       ├── preview_widget.py # Camera preview widgets
│       └── settings_panel.py # Settings configuration
├── main_window/           # Main application window
│   ├── main_window_controller.py # Main window controller
│   └── main_window_view.py       # Main window view
├── services/              # Business logic services
│   ├── interfaces/        # Service interfaces
│   ├── capture_orchestrator.py # Frame capture coordination
│   ├── config_service.py  # Configuration access service
│   ├── device_manager.py  # Camera device management
│   ├── exceptions.py      # Custom exception classes
│   ├── sequence_counter.py # Sequence number management
│   └── storage_service.py # Data storage service
├── devices/               # Camera device abstractions
│   ├── abstract_camera.py # Base camera interface
│   ├── realsense_camera.py # RealSense implementation
│   ├── zed_camera.py      # ZED camera implementation
│   └── mock_camera.py     # Mock camera for testing
├── models/                # Data models
│   ├── camera.py          # Camera and frame models
│   └── metadata.py        # Metadata models
└── main.py               # Application entry point
```

## Key Design Principles

### 1. Separation of Concerns
- **GUI Layer**: Pure presentation logic, no business logic
- **Service Layer**: Business logic and data processing
- **Device Layer**: Hardware abstraction and device communication
- **Core Layer**: Application infrastructure and utilities

### 2. Dependency Injection
- Services are registered in a central container
- Dependencies are injected rather than hard-coded
- Improves testability and maintainability

### 3. Interface-Based Design
- Services implement well-defined interfaces
- Enables easy mocking and testing
- Supports future extensibility

### 4. Comprehensive Error Handling
- Custom exception hierarchy for different error types
- Centralized error handling with user-friendly messages
- Robust validation throughout the application

### 5. Configuration Management
- Centralized configuration with type safety
- Environment-specific settings support
- Validation of configuration values

## Installation

### Prerequisites

- Python 3.9 or higher
- Intel RealSense SDK 2.0
- ZED SDK 4.2.5 or higher
- PyQt6

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd MultiCamCollector
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install camera SDKs:
   - **Intel RealSense**: Download and install from [Intel RealSense SDK](https://github.com/IntelRealSense/librealsense)
   - **ZED SDK**: Download and install from [Stereolabs ZED SDK](https://www.stereolabs.com/developers/release/)

4. Configure the application:
   - Copy `config.yaml.example` to `config.yaml`
   - Modify settings as needed

## Usage

### Running the Application

```bash
python main.py
```

### Configuration

The application uses a YAML configuration file (`config.yaml`) for settings:

```yaml
# Camera Settings
camera_resolution: "1280x720"
camera_fps: 30
exposure:
  d435i: 150
  zed2i: 100

# ZED Camera Settings
zed:
  enable_self_calibration: false
  depth_mode: "PERFORMANCE"
  depth_stabilization: true
  depth_minimum_distance: 200

# Storage Settings
dataset_root_dir: "../the-dataset"
directory_format: "{date}/{lighting}/{background_id}"

# Logging
log_level: "INFO"
log_file: "multicam_collector.log"
```

### Data Organization

Captured data is organized in a hierarchical structure:

```
the-dataset/
├── 20250709/              # Date (YYYYMMDD)
│   ├── normal/            # Lighting condition
│   │   ├── background_01/ # Background ID
│   │   │   ├── seq_001/   # Sequence number
│   │   │   │   ├── metadata.json
│   │   │   │   ├── 20250709T143022123_RealSense_123456_RGB.png
│   │   │   │   ├── 20250709T143022123_RealSense_123456_Depth.tiff
│   │   │   │   └── ...
```

## Development

### Code Style

The project follows PEP 8 coding standards with additional guidelines:

- Use type hints for all function parameters and return values
- Write comprehensive docstrings for all public methods
- Use descriptive variable and function names
- Keep functions focused and single-purpose

### Testing

Run tests using pytest:

```bash
pytest tests/
```

### Adding New Camera Types

1. Create a new camera class inheriting from `AbstractCamera`
2. Implement all required methods
3. Register the camera type in `DeviceManager`
4. Add configuration options if needed

### Extending the GUI

1. Create new widgets inheriting from `BaseWidget`
2. Use the `WidgetFactory` for dependency injection
3. Follow the MVC pattern for complex widgets
4. Add proper error handling and validation

## Troubleshooting

### Common Issues

1. **No cameras detected**: 
   - Verify camera drivers are installed
   - Check USB connections
   - Run with administrator privileges if needed

2. **Permission errors**:
   - Ensure write permissions for the dataset directory
   - Check camera access permissions

3. **Performance issues**:
   - Reduce camera resolution or FPS
   - Close other applications using cameras
   - Check available disk space

### Logging

The application creates detailed logs in the `logs/` directory. Check the latest log file for error details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes following the coding standards
4. Add tests for new functionality
5. Submit a pull request

## License

[Add your license information here]

## Acknowledgments

- Intel RealSense team for the excellent SDK
- Stereolabs for the ZED SDK
- Qt team for the robust GUI framework
