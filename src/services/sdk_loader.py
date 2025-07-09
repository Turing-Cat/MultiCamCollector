
import sys
import os
import platform

def _add_to_path(path):
    """Adds a directory to sys.path if it's not already there."""
    if path not in sys.path:
        sys.path.insert(0, path)

def load_sdk():
    """
    Detects the operating system and loads the appropriate ZED and RealSense SDK libraries.

    It prioritizes system-installed SDKs and falls back to the 'third_party' directory
    if they are not found.
    """
    system = platform.system()
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    third_party_dir = os.path.join(base_dir, 'third_party')

    if system == "Windows":
        # ZED SDK on Windows
        zed_sdk_root = os.environ.get("ZED_SDK_ROOT_DIR", "C:/Program Files (x86)/ZED SDK")
        zed_bin_path = os.path.join(zed_sdk_root, "bin")
        if os.path.isdir(zed_bin_path):
            _add_to_path(zed_bin_path)
        elif os.path.isdir(third_party_dir):
             _add_to_path(third_party_dir)


    elif system == "Linux":
        # ZED SDK on Linux
        # Typical installation path for ZED SDK on Linux
        zed_lib_path = "/usr/local/zed/lib"
        if os.path.isdir(zed_lib_path):
            _add_to_path(zed_lib_path)
        elif os.path.isdir(third_party_dir):
            _add_to_path(third_party_dir)
        
        # RealSense SDK on Linux (pyrealsense2 is often installed via pip and works,
        # but this is a fallback for manual installations or when the .so is in a custom place)
        realsense_lib_path = "/usr/lib/x86_64-linux-gnu"
        if os.path.isfile(os.path.join(realsense_lib_path, "librealsense2.so")):
             _add_to_path(realsense_lib_path)
        elif os.path.isdir(third_party_dir):
            _add_to_path(third_party_dir)


# Execute loading logic when the module is imported
load_sdk()
