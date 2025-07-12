import yaml
from typing import Dict, Any, Tuple

class ConfigService:
    """
    A centralized service to load and provide access to the application's
    configuration from config.yaml.
    """
    def __init__(self, config_path="config.yaml"):
        try:
            with open(config_path, "r") as f:
                self._config = yaml.safe_load(f)
        except (FileNotFoundError, yaml.YAMLError) as e:
            print(f"FATAL: Could not load or parse {config_path}: {e}")
            # In a real app, you might exit or use a default config
            self._config = {}

    @property
    def camera_resolution(self) -> Tuple[int, int]:
        """Returns the camera resolution as a (width, height) tuple."""
        res_str = self._config.get("camera_resolution", "640x480")
        try:
            width, height = map(int, res_str.split('x'))
            return width, height
        except ValueError:
            print(f"Warning: Invalid camera_resolution format. Using 640x480.")
            return 640, 480

    @property
    def camera_fps(self) -> int:
        """Returns the camera frames per second."""
        return int(self._config.get("camera_fps", 30))

    @property
    def zed_settings(self) -> Dict[str, Any]:
        """Returns the ZED-specific settings dictionary."""
        return self._config.get("zed", {})

    @property
    def ui_settings(self) -> Dict[str, Any]:
        """Returns the UI performance settings dictionary."""
        return self._config.get("ui", {})

    @property
    def display_fps(self) -> int:
        """Returns the UI display FPS limit."""
        return int(self.ui_settings.get("display_fps", 15))

    @property
    def frame_timeout_ms(self) -> int:
        """Returns the frame capture timeout in milliseconds."""
        return int(self.ui_settings.get("frame_timeout_ms", 500))

    @property
    def thread_stop_timeout_ms(self) -> int:
        """Returns the thread stop timeout in milliseconds."""
        return int(self.ui_settings.get("thread_stop_timeout_ms", 2000))

    def get_full_config(self) -> Dict[str, Any]:
        """Returns the entire configuration dictionary."""
        return self._config

