# hand_drawing_challenge/services/drawing_service.py
import numpy as np
import cv2
from typing import Optional, List, Tuple
from dataclasses import dataclass
from ..events.bus import EventBus
from ..events.types import DrawingEvent
from input_processing.drawing_tracker import DrawingTracker

@dataclass
class DrawingState:
    """Current state of the drawing canvas."""
    position: Optional[Tuple[int, int]]
    is_drawing: bool
    canvas: np.ndarray
    trail_points: List[Tuple[int, int]]

class DrawingService:
    """Manages drawing state and operations."""
    
    def __init__(self, event_bus: EventBus, width: int = 640, height: int = 480):
        """Initialize drawing service.
        
        Args:
            event_bus: Event bus for publishing state changes
            width: Canvas width in pixels
            height: Canvas height in pixels
        """
        self.event_bus = event_bus
        self.width = width
        self.height = height
        
        # Drawing state
        self.canvas = np.zeros((height, width, 3), dtype=np.uint8)
        self.is_drawing = False
        self.drawing_tracker = DrawingTracker(width=width, height=height)
        
    def update_drawing(self, position: Optional[Tuple[int, int]]) -> None:
        """Update drawing state with new position.
        
        Args:
            position: Current drawing position (x, y)
        """
        if not position:
            return
            
        # Update trail points
        smoothed_pos = self.drawing_tracker.update(position, self.is_drawing)
        
        if smoothed_pos and self.is_drawing:
            trail_points = self.drawing_tracker.get_trail_points()
            if len(trail_points) > 1:
                self._draw_line(trail_points[-2], trail_points[-1])
            
            # Emit state change event
            self.event_bus.publish(
                DrawingEvent.STATE_CHANGED,
                state=self.get_state()
            )
    
    def _draw_line(self, start: Tuple[int, int], end: Tuple[int, int]) -> None:
        """Draw a line on the canvas.
        
        Args:
            start: Starting point (x, y)
            end: Ending point (x, y)
        """
        cv2.line(
            self.canvas,
            start,
            end,
            (0, 255, 0),  # Green color
            2  # Line thickness
        )
    
    def set_drawing_state(self, is_drawing: bool) -> None:
        """Set whether currently drawing or not.
        
        Args:
            is_drawing: Whether to enable drawing mode
        """
        self.is_drawing = is_drawing
        self.event_bus.publish(
            DrawingEvent.MODE_CHANGED,
            is_drawing=is_drawing
        )
    
    def clear(self) -> None:
        """Clear the drawing canvas."""
        self.canvas.fill(0)
        self.drawing_tracker.clear()
        self.event_bus.publish(DrawingEvent.CANVAS_CLEARED)
    
    def get_state(self) -> DrawingState:
        """Get current drawing state.
        
        Returns:
            DrawingState: Current state of the drawing
        """
        return DrawingState(
            position=self.drawing_tracker.last_valid_position,
            is_drawing=self.is_drawing,
            canvas=self.canvas.copy(),
            trail_points=self.drawing_tracker.get_trail_points()
        )