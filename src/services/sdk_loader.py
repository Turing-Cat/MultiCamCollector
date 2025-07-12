import sys
import os
import platform

def _add_to_path(path):
    """Adds a directory to the system's PATH environment variable and Python's sys.path."""
    if path and os.path.isdir(path):
        # Add to system PATH
        os.environ["PATH"] = path + os.pathsep + os.environ.get("PATH", "")
        # Add to Python path
        if path not in sys.path:
            sys.path.insert(0, path)

def load_system_sdks():
    """
    Configures the environment to use system-installed ZED and RealSense SDKs.
    
    This function relies on the SDKs being installed in their default locations
    or having their paths correctly set in the system's environment variables.
    """
    system = platform.system()

    if system == "Windows":
        # The ZED SDK installer typically adds the 'bin' directory to the system PATH.
        # If not, this code will add it based on the ZED_SDK_ROOT_DIR environment variable.
        zed_sdk_root = os.environ.get("ZED_SDK_ROOT_DIR")
        if zed_sdk_root:
            _add_to_path(os.path.join(zed_sdk_root, "bin"))

        # The RealSense SDK installer adds its directories to the system PATH,
        # so pyrealsense2 can find the required DLLs. No explicit path handling is needed.

    elif system == "Linux":
        # On Linux, the ZED SDK installer places libraries in /usr/local/zed/lib.
        # The pyrealsense2 package installed via pip typically handles its own paths.
        # This is a fallback for cases where the loader needs a hint.
        _add_to_path("/usr/local/zed/lib")

    # For RealSense, the 'pyrealsense2' Python wrapper is the primary way to interact
    # with the SDK. It is responsible for finding the underlying 'librealsense2.so'
    # or 'realsense2.dll' file, which should be in the system path after a correct
    # SDK installation. No further action is required here for RealSense.

# Execute loading logic when the module is imported
load_system_sdks()