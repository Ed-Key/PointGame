# hand_drawing_challenge/input/processors/hand_tracking.py

from typing import Optional, Tuple, Dict, Any
import cv2
import mediapipe as mp
import numpy as np
from dataclasses import dataclass
from ...events.types import GameEventType
from ...events.bus import EventBus
from ..interfaces import InputProcessor
from ..drawing_tracker import DrawingTracker
from ..input_types import HandPoint

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

class HandTrackingProcessor(InputProcessor):
    """
    Processes hand tracking input using MediaPipe and publishes relevant events.
    Uses DrawingTracker for trail management and smoothing.
    """
    
    def __init__(self, event_bus: EventBus, config: HandProcessorConfig):
        """Initialize the hand tracking processor."""
        self.event_bus = event_bus
        self.config = config
        self._active = False
        
        # State tracking
        self.hand_detected = False
        self.is_drawing = False
        self.last_position: Optional[Tuple[int, int]] = None
        
        # Initialize MediaPipe
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=config.min_detection_confidence,
            min_tracking_confidence=config.min_tracking_confidence
        )
        
        # Initialize camera
        self.camera = cv2.VideoCapture(config.camera_id)
        if self.camera.isOpened():
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, config.camera_width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, config.camera_height)
        
        # Initialize drawing tracker
        self.drawing_tracker = DrawingTracker(
            width=config.camera_width,
            height=config.camera_height
        )
        
        # Drawing canvas
        self.canvas = np.zeros((config.camera_height, config.camera_width, 3), 
                             dtype=np.uint8)
    
    def is_active(self) -> bool:
        """Return whether the processor is active and ready."""
        return bool(self._active and self.camera and self.camera.isOpened())

    def start(self) -> None:
        """Start the processor and initialize resources."""
        if not self.is_active():
            if not self.camera.isOpened():
                self.camera = cv2.VideoCapture(self.config.camera_id)
                if not self.camera.isOpened():
                    raise RuntimeError("Failed to open camera")
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.camera_width)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.camera_height)
            self._active = True

    def stop(self) -> None:
        """Stop the processor and release resources."""
        self._active = False
        if self.camera.isOpened():
            self.camera.release()
        self.cleanup()

    def cleanup(self) -> None:
        """Clean up resources."""
        self.hands.close()
        if self.camera.isOpened():
            self.camera.release()
        
    def process(self, *args: Any, **kwargs: Any) -> Optional[np.ndarray]:
        """Process current frame and update hand tracking state."""
        if not self.is_active():
            return None
            
        success, frame = self.camera.read()
        if not success:
            self._active = False
            return None
            
        # Mirror if configured
        if self.config.mirror_camera:
            frame = cv2.flip(frame, 1)
            
        # Convert and process frame
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        # Handle hand detection state change
        if results.multi_hand_landmarks:
            if not self.hand_detected:
                self.hand_detected = True
                self.event_bus.publish(GameEventType.HAND_DETECTED)
            
            # Process hand landmarks
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # Convert to HandPoint
            h, w, _ = frame.shape
            index_tip = hand_landmarks.landmark[8]
            hand_point = HandPoint(
                x=index_tip.x,
                y=index_tip.y,
                z=index_tip.z
            )
            
            # Update drawing tracker
            smoothed_pos = self.drawing_tracker.update(hand_point, self.is_drawing)
            
            if smoothed_pos:
                # Update position and publish event
                self.last_position = smoothed_pos
                self.event_bus.publish(
                    GameEventType.HAND_POSITION_UPDATED,
                    {"position": smoothed_pos}
                )
                
                # Update drawing if active
                if self.is_drawing:
                    self._update_drawing()
                
                # Draw debug visualization
                if self.config.draw_debug:
                    color = (0, 255, 0) if self.is_drawing else (0, 0, 255)
                    cv2.circle(frame, smoothed_pos, 5, color, -1)
                    
        elif self.hand_detected:
            self.hand_detected = False
            self.last_position = None
            self.event_bus.publish(GameEventType.HAND_LOST)
        
        # Combine frame and drawing canvas
        return cv2.addWeighted(frame, 1.0, self.canvas, 0.7, 0)
        
    def _update_drawing(self) -> None:
        """Update the drawing canvas using trail points from tracker."""
        trail_points = self.drawing_tracker.get_trail_points()
        if len(trail_points) > 1:
            cv2.line(
                self.canvas,
                trail_points[-2],
                trail_points[-1],
                (0, 255, 0),
                4
            )
        
    def set_drawing_state(self, is_drawing: bool) -> None:
        """Set the drawing state and publish appropriate event."""
        if self.is_drawing != is_drawing:
            self.is_drawing = is_drawing
            event_type = (
                GameEventType.DRAWING_STARTED if is_drawing 
                else GameEventType.DRAWING_ENDED
            )
            self.event_bus.publish(event_type)
            
    def clear_canvas(self) -> None:
        """Clear the drawing canvas and tracker state."""
        self.canvas.fill(0)
        self.drawing_tracker.clear()
