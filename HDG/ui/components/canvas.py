# ui/components/canvas.py
import cv2
import numpy as np
import pygame
from ..base import UIComponent
from ..utils.colors import Colors
from input_processing.drawing_tracker import DrawingTracker
from input_processing.hand_tracking import HandPoint

class DrawingCanvas(UIComponent):
    """Component for handling drawing visualization and input."""
    
    def __init__(self, rect: pygame.Rect):
        """Initialize the drawing canvas.
        
        Args:
            rect: Position and size of the canvas
        """
        super().__init__(rect)
        self.canvas = np.zeros((rect.height, rect.width, 3), dtype=np.uint8)
        self.drawing_tracker = DrawingTracker(width=rect.width, height=rect.height)
        self.is_drawing = False
        
    def update(self, camera_frame: np.ndarray, hand_point: HandPoint) -> None:
        """Update the canvas with new input.
        
        Args:
            camera_frame: Current camera frame
            hand_point: Current hand position
        """
        # Update drawing tracker and get smoothed position
        smoothed_pos = self.drawing_tracker.update(hand_point, self.is_drawing)
        
        if smoothed_pos:
            x, y = smoothed_pos
            # Draw current position indicator
            color = Colors.DRAWING_ACTIVE if self.is_drawing else Colors.DRAWING_INACTIVE
            cv2.circle(camera_frame, (x, y), 5, color, -1)
            
            # Draw trail
            trail_points = self.drawing_tracker.get_trail_points()
            if len(trail_points) > 1:
                cv2.line(self.canvas,
                       trail_points[-2],
                       trail_points[-1],
                       Colors.TRAIL_COLOR,
                       2)
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the canvas on the screen.
        
        Args:
            screen: Pygame surface to draw on
        """
        if not self.visible:
            return
            
        # Draw canvas border
        pygame.draw.rect(screen, Colors.BORDER, self.rect, 2)
        
        # Convert canvas to pygame surface
        canvas_surface = pygame.surfarray.make_surface(
            cv2.cvtColor(self.canvas, cv2.COLOR_BGR2RGB))
        canvas_surface = pygame.transform.rotate(canvas_surface, 270)
        
        # Draw to screen
        screen.blit(canvas_surface, self.rect)
    
    def clear(self) -> None:
        """Clear the drawing canvas."""
        self.drawing_tracker.clear()
        self.canvas = np.zeros((self.rect.height, self.rect.width, 3), dtype=np.uint8)
    
    def set_drawing_state(self, is_drawing: bool) -> None:
        """Set whether currently drawing or not.
        
        Args:
            is_drawing: Whether to enable drawing mode
        """
        self.is_drawing = is_drawing
    
    def get_drawing_state(self) -> bool:
        """Get current drawing state.
        
        Returns:
            bool: Whether currently in drawing mode
        """
        return self.is_drawing