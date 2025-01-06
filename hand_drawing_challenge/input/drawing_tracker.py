# hand_drawing_challenge/input/drawing_tracker.py

from collections import deque
import numpy as np
from typing import Optional, Tuple, List, Deque
from dataclasses import dataclass
from .input_types import HandPoint

@dataclass
class DrawingConfig:
    """Configuration for drawing behavior."""
    smoothing_window: int = 5
    max_jump_distance: int = 100  # Maximum allowed position change between frames
    min_movement_threshold: int = 5  # Minimum movement to register a new point
    max_points: int = 1000  # Maximum number of points to store in trail

class DrawingTracker:
    """
    Handles drawing input processing with smoothing and stability improvements.

    Features:
    - Position smoothing using moving average
    - Jump detection to filter erratic movements
    - Minimum movement threshold to reduce jitter
    - Trail point management
    """

    def __init__(self,
                 width: int = 640,
                 height: int = 480,
                 config: Optional[DrawingConfig] = None):
        """
        Initialize the drawing tracker.

        Args:
            width: Canvas width in pixels
            height: Canvas height in pixels
            config: Optional drawing configuration settings
        """
        self.width = width
        self.height = height
        self.config = config or DrawingConfig()

        # Position tracking
        self.position_history: Deque[Tuple[int, int]] = deque(
            maxlen=self.config.smoothing_window
        )
        self.last_valid_position: Optional[Tuple[int, int]] = None

        # Trail management
        self.trail_points: List[Tuple[int, int]] = []

    def update(self,
              hand_point: Optional[HandPoint],
              is_drawing: bool) -> Optional[Tuple[int, int]]:
        """
        Update the drawing tracker with new hand position.

        Args:
            hand_point: New hand position from tracker
            is_drawing: Whether currently in drawing mode

        Returns:
            Current smoothed position or None if invalid
        """
        # Process new position
        smoothed_position = self._smooth_position(hand_point)

        if smoothed_position and is_drawing:
            if self._should_add_point(smoothed_position):
                self._add_trail_point(smoothed_position)

        return smoothed_position

    def _smooth_position(self, hand_point: Optional[HandPoint]) -> Optional[Tuple[int, int]]:
        """
        Smooth the hand position using a moving average and validate movement.

        Args:
            hand_point: New hand position from tracker

        Returns:
            Smoothed and validated (x, y) position or None if invalid
        """
        if hand_point is None:
            return self.last_valid_position

        # Convert normalized coordinates to pixel coordinates
        x = int(hand_point.x * self.width)
        y = int(hand_point.y * self.height)

        # Validate position is within bounds
        if not (0 <= x < self.width and 0 <= y < self.height):
            return self.last_valid_position

        # Check for unrealistic jumps if we have a previous position
        if self.last_valid_position:
            last_x, last_y = self.last_valid_position
            distance = np.sqrt((x - last_x)**2 + (y - last_y)**2)
            if distance > self.config.max_jump_distance:
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
        """
        Determine if a new point should be added to the trail.

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

        return distance >= self.config.min_movement_threshold

    def _add_trail_point(self, position: Tuple[int, int]) -> None:
        """
        Add a point to the trail, maintaining maximum length.

        Args:
            position: Position to add to trail
        """
        self.trail_points.append(position)
        if len(self.trail_points) > self.config.max_points:
            self.trail_points.pop(0)

    def get_trail_points(self) -> List[Tuple[int, int]]:
        """
        Get the current trail points.

        Returns:
            List of (x, y) coordinates making up the trail
        """
        return self.trail_points

    def clear(self) -> None:
        """Clear the drawing trail and reset state."""
        self.trail_points.clear()
        self.position_history.clear()
        self.last_valid_position = None

    def get_last_position(self) -> Optional[Tuple[int, int]]:
        """
        Get the last valid hand position.

        Returns:
            Last valid (x, y) position or None if no position available
        """
        return self.last_valid_position

    def get_drawing_metrics(self) -> dict:
        """
        Get metrics about the current drawing.

        Returns:
            Dictionary containing:
            - point_count: Number of points in trail
            - trail_length: Approximate length of trail in pixels
            - bounds: (min_x, min_y, max_x, max_y) of trail
        """
        if not self.trail_points:
            return {
                'point_count': 0,
                'trail_length': 0,
                'bounds': (0, 0, 0, 0)
            }

        # Calculate trail length
        length = 0
        for i in range(1, len(self.trail_points)):
            x1, y1 = self.trail_points[i-1]
            x2, y2 = self.trail_points[i]
            length += np.sqrt((x2-x1)**2 + (y2-y1)**2)

        # Calculate bounds
        points = np.array(self.trail_points)
        min_x, min_y = np.min(points, axis=0)
        max_x, max_y = np.max(points, axis=0)

        return {
            'point_count': len(self.trail_points),
            'trail_length': int(length),
            'bounds': (int(min_x), int(min_y), int(max_x), int(max_y))
        }
