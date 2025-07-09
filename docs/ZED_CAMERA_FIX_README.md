# ZED Camera Self-Calibration Fix

## Problem Description

The ZED camera was showing a self-calibration warning:
```
[Init] Self-calibration failed. Point the camera towards a more textured and brighter area. Avoid objects closer than 1 meter (Error code: 0x01)
```

This warning appeared because the ZED SDK was trying to perform automatic self-calibration during initialization, but the camera environment didn't meet the requirements for successful calibration.

## Solution Implemented

### 1. Disabled Self-Calibration by Default
- Modified `ZedCamera.__init__()` to set `enable_self_calib = False`
- This prevents the warning from appearing during normal operation
- The camera still works perfectly with factory calibration

### 2. Enhanced Error Handling
- Added comprehensive error handling in `ZedCamera.connect()`
- Provides specific error messages for different connection issues
- Gracefully handles calibration status reporting

### 3. Optional Self-Calibration
- Added `enable_self_calibration()` method for manual calibration
- Provides user guidance for optimal calibration conditions
- Falls back to factory calibration if self-calibration fails

### 4. Calibration Status Tracking
- Added `calibration_status` property to track calibration state
- Provides user guidance through `get_calibration_guidance()` method
- Integration with DeviceManager for status reporting

## Usage

### Basic Usage (No Warning)
The camera now connects without any self-calibration warnings:

```python
from devices.zed_camera import ZedCamera

camera = ZedCamera(camera_id="ZED_33334385", serial_number="33334385")
camera.connect()  # No warning!
print(f"Calibration status: {camera.calibration_status}")
```

### Manual Self-Calibration (Optional)
If you want better depth accuracy, you can manually trigger self-calibration:

```python
# After connecting the camera
success = camera.enable_self_calibration()
if success:
    print("Self-calibration successful!")
else:
    print("Self-calibration failed, using factory calibration")
```

### Device Manager Integration
The DeviceManager now provides calibration management:

```python
from services.device_manager import DeviceManager

device_manager = DeviceManager()
device_manager.discover_cameras()

# Get calibration status for all ZED cameras
status = device_manager.get_zed_calibration_status()
print(status)

# Trigger calibration for all ZED cameras
device_manager.calibrate_zed_cameras()
```

## Configuration

You can control ZED camera behavior through `config.yaml`:

```yaml
# ZED Camera Settings
zed:
  enable_self_calibration: false  # Set to true to enable self-calibration on startup
  depth_mode: "PERFORMANCE"       # Options: PERFORMANCE, QUALITY, ULTRA, NEURAL
  depth_stabilization: true
  depth_minimum_distance: 200     # Minimum depth distance in mm
```

## Testing

Run the test script to verify the fix:

```bash
python test_zed_fix.py
```

This script will:
1. Test direct ZED camera connection
2. Test camera discovery through DeviceManager
3. Optionally test self-calibration functionality

## When to Use Self-Calibration

**Use factory calibration (default) when:**
- You need quick, reliable camera operation
- The environment changes frequently
- You're doing general RGB-D capture

**Use self-calibration when:**
- You need maximum depth accuracy
- The camera setup is fixed/permanent
- You have a controlled environment with good lighting and textures

## Calibration Environment Requirements

For successful self-calibration:
- **Lighting**: Bright, even lighting (avoid shadows)
- **Texture**: Point camera at textured surfaces (books, posters, patterns)
- **Distance**: Keep objects at least 1 meter away
- **Stability**: Keep camera steady during calibration process

## Error Codes and Troubleshooting

| Error Code | Meaning | Solution |
|------------|---------|----------|
| `CAMERA_NOT_DETECTED` | USB connection issue | Check USB cable and ports |
| `CAMERA_DETECTION_ISSUE` | Driver/hardware issue | Reconnect camera, restart app |
| `INVALID_FUNCTION_PARAMETERS` | Wrong serial number | Verify camera serial number |
| Self-calibration warning | Environment not suitable | Follow calibration guidelines above |

## Files Modified

1. `devices/zed_camera.py` - Enhanced ZED camera implementation
2. `services/device_manager.py` - Added calibration management
3. `config.yaml` - Added ZED camera configuration options
4. `test_zed_fix.py` - Test script for verification

## Benefits of This Fix

1. **No More Warnings**: Clean startup without calibration warnings
2. **Better Error Handling**: Clear error messages for troubleshooting
3. **Flexible Calibration**: Choose when and how to calibrate
4. **User Guidance**: Clear instructions for optimal calibration
5. **Backward Compatible**: Existing code continues to work
6. **Configurable**: Control behavior through configuration files

The ZED camera now provides a much better user experience with reliable operation and optional advanced features when needed.
