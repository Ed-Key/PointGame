# Initialize the input_processing package

# Import specific classes/functions to make them available directly
from .camera import Camera, CameraConfig, CameraError
from .hand_tracking import HandTracker

# Optionally define an __all__ list to control what gets imported with `from input_processing import *`
__all__ = [
    "Camera",
    "CameraConfig",
    "CameraError",
    "HandTracker"
]
