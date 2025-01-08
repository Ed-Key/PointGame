"""
hand_drawing_challenge/input/processors/hand_tracking.py

Implements HandTrackingProcessor, an InputProcessor that:
- Opens camera with cv2.VideoCapture
- Uses MediaPipe to detect hand landmarks
- Publishes hand detection events
"""

import cv2
import mediapipe as mp
import numpy as np
import logging
from dataclasses import dataclass
from typing import Optional, Tuple, Any

# Adjust the imports below if your structure differs:
from hand_drawing_challenge.events.bus import EventBus
from hand_drawing_challenge.events.types import GameEventType
from hand_drawing_challenge.input.interfaces import InputProcessor
from hand_drawing_challenge.input.input_types import HandPoint


@dataclass
class HandProcessorConfig:
    """Configuration for hand tracking processor."""
    min_detection_confidence: float = 0.3
    min_tracking_confidence: float = 0.3
    camera_width: int = 640
    camera_height: int = 480
    camera_id: int = 0
    mirror_camera: bool = True
    draw_debug: bool = True
    target_fps: int = 60

class HandTrackingProcessor(InputProcessor):
    """
    Processes hand tracking input using MediaPipe and publishes relevant events.
    """
    
    def __init__(self, event_bus: EventBus, config: HandProcessorConfig):
        print(">>> hand_tracking_processor.py: HandTrackingProcessor.__init__ CALLED")
        self.logger = logging.getLogger(__name__)
        self.event_bus = event_bus
        self.config = config
        self._active = False

        # Processing state
        self._processing_enabled = False
        self._camera_initialized = False
        
        # State tracking
        self.hand_detected = False
        self.is_drawing = False
        self.last_position: Optional[Tuple[int, int]] = None
        
        # Subscribe to drawing events
        self.event_bus.subscribe(GameEventType.DRAWING_STARTED, self._handle_drawing_event)
        self.event_bus.subscribe(GameEventType.DRAWING_ENDED, self._handle_drawing_event)
        
        # Initialize camera and MediaPipe Hands
        self.camera = None
        self.hands = None
        self.mp_hands = mp.solutions.hands

        # Initialize camera on startup
        self._initialize_camera()
        self._initialize_mediapipe()
    
    def _initialize_mediapipe(self) -> bool:
        """Initialize MediaPipe hands."""
        try:
            if self.hands is None:
                self.logger.debug("Creating MediaPipe Hands instance")
                self.hands = self.mp_hands.Hands(
                    static_image_mode=False,
                    max_num_hands=1,
                    min_detection_confidence=self.config.min_detection_confidence,
                    min_tracking_confidence=self.config.min_tracking_confidence
                )
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize MediaPipe: {e}")
            return False

    def _initialize_camera(self) -> None:
        """Initialize the camera but don't start it yet"""
        if self._camera_initialized:
            return True
        try:
            self.logger.info(f"Attempting to open camera {self.config.camera_id}")
            self.camera = cv2.VideoCapture(self.config.camera_id)
            if not self.camera.isOpened():
                self.logger.error(f"Failed to open camera {self.config.camera_id}!")
                return
            
            # Set and verify camera properties
            self.logger.info("Setting camera properties...")
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.camera_width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.camera_height)
            self.camera.set(cv2.CAP_PROP_FPS, self.config.target_fps)

            # Read actual properties
            w = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
            h = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
            fps = self.camera.get(cv2.CAP_PROP_FPS)
            backend = self.camera.getBackendName()
            
            self.logger.info(f"Camera initialized with:")
            self.logger.info(f"- Resolution: {w}x{h}")
            self.logger.info(f"- FPS: {fps}")
            self.logger.info(f"- Backend: {backend}")
            
            # Test frame capture
            success, test_frame = self.camera.read()
            if success and test_frame is not None:
                self.logger.info(f"Test frame captured successfully: shape={test_frame.shape}, dtype={test_frame.dtype}")
                self._active = True
            else:
                self.logger.error("Failed to capture test frame!")
                self.camera.release()
                self.camera = None

            self._camera_initialized = True

        except Exception as e:
            self.logger.error(f"Exception opening camera: {e}")
            if self.camera:
                self.camera.release()
                self.camera = None

    def is_active(self) -> bool:
        """Return whether the processor is active and camera is open."""
        return bool(self._active and self.camera and self.camera.isOpened())

    def start(self) -> None:
        """Start the processor."""
        self.logger.info("Starting hand tracking processor")
        if not self._camera_initialized:
            self._initialize_camera()
        if not self.hands:
            self._initialize_mediapipe()

        self._active = True
        self.logger.info("Hand tracking processor started successfully")

    def stop(self) -> None:
        """Stop processing but keep camera alive."""
        self.logger.info("Stopping hand tracking processing")
        self._processing_enabled = False
        self.hand_detected = False
        self.last_position = None

        # Reset MediaPipe but keep camera
        if self.hands:
            self.hands.close()
            self.hands = None

    def cleanup(self) -> None:
        """Final cleanup - only called when application exits."""
        self.logger.info("Cleaning up hand tracking processor")
        try:
            if self.hands:
                self.hands.close()
                self.hands = None
            
            if self.camera:
                self.camera.release()
                self.camera = None
            
            self._camera_initialized = False
            self._processing_enabled = False
            self.hand_detected = False
            self.last_position = None
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def enable_processing(self) -> None:
        """Enable frame processing."""
        self.logger.info("Enabling hand tracking processing")
        if not self.hands:
            self._initialize_mediapipe()
        self._processing_enabled = True

    def disable_processing(self) -> None:
        """Disable frame processing but keep camera alive."""
        self.logger.info("Disabling hand tracking processing")
        self._processing_enabled = False
        if self.hand_detected:
            self.hand_detected = False
            self.last_position = None
            self.event_bus.publish(GameEventType.HAND_LOST)
    
    def process(self, *args: Any, **kwargs: Any) -> Optional[np.ndarray]:
        """Process the current frame and update hand tracking state.

        Returns:
            The camera frame (with debug overlays if draw_debug=True),
            or None if the camera read fails or not active.
        """
        if not self._camera_initialized or not self._processing_enabled:
            return None
            
        try:
            success, frame = self.camera.read()
            if not success or frame is None:
                return None
            
            if self.config.mirror_camera:
                frame = cv2.flip(frame, 1)
            
            # Only process hand detection if enabled
            if self._processing_enabled and self.hands:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.hands.process(rgb_frame)
                
                # Update hand tracking state and publish events
                self._process_hand_detection(results, frame.shape[:2])
                
                # Draw debug visualization if enabled
                if self.config.draw_debug:
                    frame = self._draw_debug(frame, results)
            
            return frame
            
        except Exception as e:
            self.logger.error(f"Error processing frame: {e}")
            return None
    
    def _process_hand_detection(self, results: Any, frame_shape: Tuple[int, int]) -> None:
        """Process hand detection results and publish events."""
        h, w = frame_shape
        
        if results.multi_hand_landmarks:
            if not self.hand_detected:
                self.hand_detected = True
                self.event_bus.publish(GameEventType.HAND_DETECTED)
            
            landmarks = results.multi_hand_landmarks[0].landmark
            index_tip = landmarks[8]
            
            x = int(index_tip.x * w)
            y = int(index_tip.y * h)
            self.last_position = (x, y)
            
            # Create and publish hand point event
            hand_point = HandPoint(x=index_tip.x, y=index_tip.y, z=index_tip.z)
            self.event_bus.publish(
                GameEventType.HAND_POSITION_UPDATED,
                {
                    "position": hand_point,
                    "is_drawing": self.is_drawing,
                    "frame_dimensions": (w, h)
                }
            )
        else:
            if self.hand_detected:
                self.hand_detected = False
                self.last_position = None
                self.event_bus.publish(GameEventType.HAND_LOST)


    def _draw_debug(self, frame: np.ndarray, results: Any) -> np.ndarray:
        """Draw debug visualization on the frame."""
        debug_frame = frame.copy()
        if results.multi_hand_landmarks:
            if self.last_position:
                h, w = frame.shape[:2]
                x = int(self.last_position[0])
                y = int(self.last_position[1])
                color = (0, 255, 0) if self.is_drawing else (0, 0, 255)
                cv2.circle(debug_frame, (x, y), 5, color, -1)
        return debug_frame
            
    def _handle_drawing_event(self, event_type: GameEventType, data: Optional[dict] = None) -> None:
        """Handle drawing state change events."""
        self.is_drawing = (event_type == GameEventType.DRAWING_STARTED)
        self.logger.info(f"Drawing state changed to: {self.is_drawing}")

    def set_drawing_state(self, is_drawing: bool) -> None:
        """Enable or disable drawing mode."""
        if self.is_drawing != is_drawing:
            self.is_drawing = is_drawing
            event_type = (GameEventType.DRAWING_STARTED if is_drawing 
                          else GameEventType.DRAWING_ENDED)
            self.event_bus.publish(event_type)
