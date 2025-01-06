# input_processing/hand_tracking.py
import mediapipe as mp
import numpy as np
import cv2
from dataclasses import dataclass
from typing import Optional, Tuple, Any

@dataclass
class HandPoint:
    """Represents a specific point on the hand (like index fingertip).
    
    Attributes:
        x (float): x-coordinate (0-1)
        y (float): y-coordinate (0-1)
        z (float): z-coordinate (depth)
    """
    x: float
    y: float
    z: float

class HandTracker:
    """Tracks hand landmarks using MediaPipe, focused on index finger tracking."""
    
    def __init__(
        self,
        min_detection_confidence: float = 0.7,
        min_tracking_confidence: float = 0.5,
        hands_module: Any = None
    ):
        """Initialize the hand tracker.
        
        Args:
            min_detection_confidence: Minimum confidence for hand detection
            min_tracking_confidence: Minimum confidence for landmark tracking
            hands_module: MediaPipe hands module (for testing)
        """
        hands = hands_module if hands_module is not None else mp.solutions.hands
        self._mp_hands = hands.Hands(
            static_image_mode=False,
            max_num_hands=1,  # Only track one hand for drawing
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
    
    def get_index_finger_tip(self, frame) -> Optional[HandPoint]:
        """Get the position of the index finger tip.
        
        Args:
            frame: Video frame from camera
            
        Returns:
            HandPoint if index finger is detected, None otherwise
        """
        # Convert the BGR image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = self._mp_hands.process(rgb_frame)
            
        # Check if any hands were detected
        if not results.multi_hand_landmarks:
            return None
            
        # Get the first hand detected
        hand_landmarks = results.multi_hand_landmarks[0]
        
        # Index fingertip is landmark 8 in MediaPipe Hands
        index_tip = hand_landmarks.landmark[8]
        
        return HandPoint(
            x=index_tip.x,
            y=index_tip.y,
            z=index_tip.z
        )
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._mp_hands.close()
