# input_processing/camera.py
import cv2
import numpy as np
from dataclasses import dataclass
from typing import Tuple, Optional

@dataclass
class CameraConfig:
    """Configuration for camera setup.
    
    Attributes:
        width (int): Frame width in pixels
        height (int): Frame height in pixels
        fps (int): Target frames per second
        device_id (int): Camera device identifier
        mirror (bool): Whether to mirror the camera feed horizontally
    """
    width: int = 640
    height: int = 480
    fps: int = 60
    device_id: int = 0
    mirror: bool = True

class CameraError(Exception):
    """Custom exception for camera-related errors."""
    pass

class Camera:
    """Manages camera operations for input capture."""
    
    def __init__(self, config: CameraConfig = CameraConfig()):
        """Initialize camera with given configuration."""
        print("[Camera] Creating new Camera instance") # Debug print
        self.config = config
        self._capture = None
        self._is_running = False
    
    def start(self) -> None:
        """Start the camera capture."""
        print("[Camera] Attempting to start camera...") # Debug print
        try:
            if self._is_running:
                print("[Camera] Camera is already running") # Debug print
                return
            
            print(f"[Camera] Opening camera device {self.config.device_id}") # Debug print
            self._capture = cv2.VideoCapture(self.config.device_id)
            
            if not self._capture.isOpened():
                print("[Camera] Failed to open camera device") # Debug print
                raise CameraError(f"Failed to open camera device {self.config.device_id}")
            
            print("[Camera] Setting camera properties...") # Debug print
            self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.width)
            self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.height)
            self._capture.set(cv2.CAP_PROP_FPS, self.config.fps)
            
            # Verify camera is working
            print("[Camera] Testing frame capture...") # Debug print
            success, _ = self._capture.read()
            if not success:
                print("[Camera] Failed to capture test frame") # Debug print
                raise CameraError("Failed to capture initial frame")
            
            print("[Camera] Camera initialized successfully") # Debug print
            self._is_running = True
            
        except Exception as e:
            print(f"[Camera] Start failed with error: {str(e)}") # Debug print
            self._is_running = False
            if self._capture is not None:
                self._capture.release()
                self._capture = None
            raise CameraError(f"Camera initialization failed: {str(e)}")
    
    def get_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Capture a single frame from the camera.
        
        Returns:
            Tuple[bool, Optional[np.ndarray]]: Success flag and frame (if successful)
        """
        if not self._is_running:
            raise CameraError("Camera is not started")
        
        try:
            success, frame = self._capture.read()
            if not success:
                print("[Camera] Failed to capture frame") # Debug print
                return False, None
                
            # Mirror the frame if configured
            if self.config.mirror:
                frame = cv2.flip(frame, 1)
                
            return True, frame
        except Exception as e:
            print(f"[Camera] Frame capture failed: {str(e)}") # Debug print
            raise CameraError(f"Frame capture failed: {str(e)}")
    
    def stop(self) -> None:
        """Stop the camera and release resources."""
        print("[Camera] Stopping camera...") # Debug print
        if self._capture is not None:
            self._capture.release()
            self._is_running = False
            print("[Camera] Camera stopped successfully") # Debug print
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()