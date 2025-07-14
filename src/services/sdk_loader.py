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
    Configures the environment to use system-installed RealSense SDK.
    
    This function relies on the SDKs being installed in their default locations
    or having their paths correctly set in the system's environment variables.
    """
    system = platform.system()

    if system == "Windows":
        # The RealSense SDK installer adds its directories to the system PATH,
        # so pyrealsense2 can find the required DLLs. No explicit path handling is needed.
        pass

    elif system == "Linux":
        # The pyrealsense2 package installed via pip typically handles its own paths.
        pass

    # For RealSense, the 'pyrealsense2' Python wrapper is the primary way to interact
    # with the SDK. It is responsible for finding the underlying 'librealsense2.so'
    # or 'realsense2.dll' file, which should be in the system path after a correct
    # SDK installation. No further action is required here for RealSense.

# Execute loading logic when the module is imported
load_system_sdks()