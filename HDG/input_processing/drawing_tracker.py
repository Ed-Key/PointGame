from collections import deque
import numpy as np
from typing import Optional, Tuple, List
from .hand_tracking import HandPoint

class DrawingTracker:
    """Handles drawing input processing with smoothing and stability improvements."""
    
    def __init__(self, 
                 width: int = 640, 
                 height: int = 480,
                 smoothing_window: int = 5,
                 max_jump_distance: int = 100,
                 min_movement_threshold: int = 5):
        """Initialize the drawing tracker.
        
        Args:
            width: Canvas width in pixels
            height: Canvas height in pixels
            smoothing_window: Number of frames to use for position smoothing
            max_jump_distance: Maximum allowed position change between frames
            min_movement_threshold: Minimum movement to register a new point
        """
        self.width = width
        self.height = height
        self.trail_points: List[Tuple[int, int]] = []
        
        # Position smoothing
        self.smoothing_window = smoothing_window
        self.position_history = deque(maxlen=smoothing_window)
        self.last_valid_position: Optional[Tuple[int, int]] = None
        
        # Stability settings
        self.max_jump_distance = max_jump_distance
        self.min_movement_threshold = min_movement_threshold
    
    def _smooth_position(self, new_point: Optional[HandPoint]) -> Optional[Tuple[int, int]]:
        """Smooth the hand position using a moving average and validate movement.
        
        Args:
            new_point: New hand position from tracker
            
        Returns:
            Smoothed and validated (x, y) position or None if invalid
        """
        if new_point is None:
            return self.last_valid_position
            
        # Convert normalized coordinates to pixel coordinates
        x = int(new_point.x * self.width)
        y = int(new_point.y * self.height)
        
        # Validate position is within bounds
        if not (0 <= x < self.width and 0 <= y < self.height):
            return self.last_valid_position
            
        # Check for unrealistic jumps if we have a previous position
        if self.last_valid_position:
            last_x, last_y = self.last_valid_position
            distance = np.sqrt((x - last_x)**2 + (y - last_y)**2)
            if distance > self.max_jump_distance:
                return self.last_valid_position
        
        # Add to position history
        self.position_history.append((x, y))
        
        # Calculate smoothed position
        if len(self.position_history) >= 3:  # Need at least 3 points for stable smoothing
            x_smooth = int(np.mean([p[0] for p in self.position_history]))
            y_smooth = int(np.mean([p[1] for p in self.position_history]))
            
            # Update last valid position
            self.last_valid_position = (x_smooth, y_smooth)
            return x_smooth, y_smooth
            
        return x, y
    
    def _should_add_point(self, new_position: Tuple[int, int]) -> bool:
        """Determine if a new point should be added to the trail.
        
        Args:
            new_position: New smoothed position
            
        Returns:
            True if point should be added, False otherwise
        """
        if not self.trail_points:
            return True
            
        last_x, last_y = self.trail_points[-1]
        new_x, new_y = new_position
        distance = np.sqrt((new_x - last_x)**2 + (new_y - last_y)**2)
        
        return distance >= self.min_movement_threshold

    def update(self, hand_point: Optional[HandPoint], is_drawing: bool) -> Optional[Tuple[int, int]]:
        """Update the drawing tracker with new hand position.
        
        Args:
            hand_point: New hand position from tracker
            is_drawing: Whether currently in drawing mode
            
        Returns:
            Current smoothed position or None if invalid
        """
        smoothed_position = self._smooth_position(hand_point)
        
        if smoothed_position and is_drawing:
            if self._should_add_point(smoothed_position):
                self.trail_points.append(smoothed_position)
        
        return smoothed_position
    
    def clear(self):
        """Clear the drawing trail and reset state."""
        self.trail_points = []
        self.position_history.clear()
        self.last_valid_position = None

    def get_trail_points(self) -> List[Tuple[int, int]]:
        """Get the current trail points.
        
        Returns:
            List of (x, y) coordinates making up the trail
        """
        return self.trail_points