# hand_drawing_challenge/input/drawing_tracker.py

from collections import deque
import numpy as np
import logging
from typing import Optional, Tuple, List, Deque, Dict
from dataclasses import dataclass
from .input_types import HandPoint

@dataclass
class DrawingConfig:
    """Configuration for drawing behavior with enhanced smoothing parameters.
    
    Attributes:
        position_history_size: Number of recent positions to keep for smoothing
        velocity_history_size: Number of recent velocities to track
        max_velocity: Maximum allowed velocity between points (pixels/frame)
        min_movement: Minimum movement to register new point (pixels)
        max_gap_distance: Maximum distance to interpolate between points (pixels)
        max_points: Maximum number of points to store in trail
        interpolation_steps: Number of points to interpolate in gaps
        smoothing_factor: Weight given to smoothed vs raw positions (0-1)
        prediction_weight: Weight given to velocity predictions (0-1)
    """
    # Position smoothing
    position_history_size: int = 15
    velocity_history_size: int = 8
    
    # Movement thresholds
    max_velocity: float = 100.0
    min_movement: float = 3.0
    max_gap_distance: float = 50.0
    
    # Trail management
    max_points: int = 10000
    interpolation_steps: int = 5
    
    # Smoothing weights
    smoothing_factor: float = 0.8
    prediction_weight: float = 0.2

class DrawingTracker:
    """Enhanced drawing tracker with improved smoothing and interpolation.
    
    Features:
    - Advanced position smoothing using weighted averaging and velocity prediction
    - Velocity-based movement filtering
    - Gap interpolation for smooth drawing
    - Configurable smoothing and filtering parameters
    """
    
    def __init__(self, width: int = 640, height: int = 480, 
                 config: Optional[DrawingConfig] = None):
        """Initialize the drawing tracker.
        
        Args:
            width: Canvas width in pixels
            height: Canvas height in pixels
            config: Optional configuration settings
        """
        self.logger = logging.getLogger(__name__)
        self.width = width
        self.height = height
        self.config = config or DrawingConfig()
        
        # Position tracking
        self.position_history: Deque[Tuple[float, float]] = deque(
            maxlen=self.config.position_history_size
        )
        self.velocity_history: Deque[Tuple[float, float]] = deque(
            maxlen=self.config.velocity_history_size
        )
        
        # State tracking
        self.last_position: Optional[Tuple[float, float]] = None
        self.last_velocity: Optional[Tuple[float, float]] = None
        self.trail_points: List[Tuple[int, int]] = []
        
        self.logger.info(f"Initialized DrawingTracker with dimensions {width}x{height}")
    
    def update(self, position: Optional[Tuple[int, int]], 
               is_drawing: bool) -> Optional[Tuple[int, int]]:
        """Update drawing state with enhanced smoothing and interpolation.
        
        Args:
            position: New position in pixel coordinates (x, y)
            is_drawing: Whether currently in drawing mode
            
        Returns:
            Smoothed position or None if position invalid
        """
        if not position:
            return self.last_position
            
        try:
            x, y = float(position[0]), float(position[1])
            
            # Basic bounds checking
            if not (0 <= x < self.width and 0 <= y < self.height):
                self.logger.debug(f"Position {position} out of bounds")
                return self.last_position
                
            # Calculate velocity if we have a previous position
            current_velocity = None
            if self.last_position:
                dx = x - self.last_position[0]
                dy = y - self.last_position[1]
                current_velocity = (dx, dy)
                
                # Check for unrealistic movements
                velocity_magnitude = np.sqrt(dx*dx + dy*dy)
                if velocity_magnitude > self.config.max_velocity:
                    self.logger.debug(
                        f"Velocity {velocity_magnitude:.2f} exceeds max {self.config.max_velocity}"
                    )
                    return self.last_position
            
            # Update histories
            self.position_history.append((x, y))
            if current_velocity:
                self.velocity_history.append(current_velocity)
            
            # Apply Kalman-inspired smoothing
            smoothed_position = self._smooth_position()
            if not smoothed_position:
                return self.last_position
                
            if is_drawing:
                self._update_trail(smoothed_position)
                
            self.last_position = smoothed_position
            return smoothed_position
            
        except Exception as e:
            self.logger.error(f"Error updating position: {e}")
            return self.last_position
    
    def _smooth_position(self) -> Optional[Tuple[float, float]]:
        """Apply advanced position smoothing using weighted averaging.
        
        Returns:
            Smoothed (x, y) position or None if insufficient history
        """
        if len(self.position_history) < 3:
            return self.position_history[-1] if self.position_history else None
            
        try:
            # Calculate weighted average of positions (more weight to recent positions)
            weights = np.linspace(
                1 - self.config.smoothing_factor,
                1.0,
                len(self.position_history)
            )
            weights = weights / weights.sum()
            
            x_smooth = y_smooth = 0.0
            for (x, y), weight in zip(self.position_history, weights):
                x_smooth += x * weight
                y_smooth += y * weight
                
            # Apply velocity-based prediction
            if self.velocity_history:
                avg_velocity = np.mean(self.velocity_history, axis=0)
                x_smooth = (x_smooth * (1 - self.config.prediction_weight) + 
                          (x_smooth + avg_velocity[0]) * self.config.prediction_weight)
                y_smooth = (y_smooth * (1 - self.config.prediction_weight) + 
                          (y_smooth + avg_velocity[1]) * self.config.prediction_weight)
                
            return (int(x_smooth), int(y_smooth))
            
        except Exception as e:
            self.logger.error(f"Error smoothing position: {e}")
            return None
    
    def _update_trail(self, new_position: Tuple[float, float]) -> None:
        """Update trail points with interpolation for gaps.
        
        Args:
            new_position: New smoothed position to add to trail
        """
        try:
            if not self.trail_points:
                self.trail_points.append(new_position)
                return
                
            last_point = self.trail_points[-1]
            distance = np.sqrt(
                (new_position[0] - last_point[0])**2 +
                (new_position[1] - last_point[1])**2
            )
            
            # Skip if movement is too small (reduces jitter)
            if distance < self.config.min_movement:
                return
                
            # Interpolate if gap is too large
            if distance > self.config.max_gap_distance:
                self._interpolate_gap(last_point, new_position)
            else:
                self.trail_points.append(new_position)
                
            # Maintain maximum trail length
            if len(self.trail_points) > self.config.max_points:
                self.trail_points = self.trail_points[-self.config.max_points:]
                
        except Exception as e:
            self.logger.error(f"Error updating trail: {e}")
    
    def _interpolate_gap(self, start: Tuple[float, float], 
                        end: Tuple[float, float]) -> None:
        """Interpolate points between gaps in the trail.
        
        Args:
            start: Starting point of the gap
            end: Ending point of the gap
        """
        try:
            for i in range(1, self.config.interpolation_steps + 1):
                t = i / (self.config.interpolation_steps + 1)
                x = start[0] + (end[0] - start[0]) * t
                y = start[1] + (end[1] - start[1]) * t
                self.trail_points.append((int(x), int(y)))
                
        except Exception as e:
            self.logger.error(f"Error interpolating gap: {e}")
    
    def clear(self) -> None:
        """Reset the drawing state."""
        self.trail_points.clear()
        self.position_history.clear()
        self.velocity_history.clear()
        self.last_position = None
        self.last_velocity = None
        self.logger.info("Drawing state cleared")
    
    def get_trail_points(self) -> List[Tuple[int, int]]:
        """Get the current trail points.
        
        Returns:
            List of (x, y) coordinates making up the trail
        """
        return self.trail_points

    def get_drawing_metrics(self) -> Dict:
        """Get metrics about the current drawing.
        
        Returns:
            Dictionary containing:
            - point_count: Number of points in trail
            - trail_length: Approximate length of trail in pixels
            - bounds: (min_x, min_y, max_x, max_y) of trail
            - smoothing_stats: Information about position smoothing
        """
        try:
            if not self.trail_points:
                return {
                    'point_count': 0,
                    'trail_length': 0,
                    'bounds': (0, 0, 0, 0),
                    'smoothing_stats': {
                        'position_history_size': len(self.position_history),
                        'velocity_history_size': len(self.velocity_history)
                    }
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
                'bounds': (int(min_x), int(min_y), int(max_x), int(max_y)),
                'smoothing_stats': {
                    'position_history_size': len(self.position_history),
                    'velocity_history_size': len(self.velocity_history),
                    'current_velocity': self.last_velocity
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating metrics: {e}")
            return {}