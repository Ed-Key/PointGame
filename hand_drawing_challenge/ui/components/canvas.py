# hand_drawing_challenge/ui/components/canvas.py

import cv2
import numpy as np
import pygame
import logging
from typing import Optional, Tuple, Union
from ..base import UIComponent
from ..utils.colors import Colors
from ...input.input_types import HandPoint
from ...input.drawing_tracker import DrawingTracker, DrawingConfig

class DrawingCanvas(UIComponent):
    """Drawing canvas component that displays camera feed and drawing visualization."""
    
    def __init__(self, rect: pygame.Rect):
        """Initialize the drawing canvas."""
        super().__init__(rect)
        self.logger = logging.getLogger(__name__)
        
        # State
        self.is_drawing = False
        self.current_frame: Optional[np.ndarray] = None
        self.last_position: Optional[Tuple[int, int]] = None
        
        # Create blank frame
        self.blank_frame = np.zeros((rect.height, rect.width, 3), dtype=np.uint8)
        
        # Initialize drawing tracker with optimized settings
        drawing_config = DrawingConfig(
            position_history_size=20,    # Increased for smoother lines
            velocity_history_size=10,    # More velocity history
            max_velocity=80.0,          # Adjusted for typical hand movement
            min_movement=4.0,           # Reduced jitter
            max_gap_distance=40.0,      # Conservative gap filling
            interpolation_steps=6,      # Smoother interpolation
            smoothing_factor=0.85,      # Strong smoothing
            prediction_weight=0.15      # Modest prediction influence
        )
        
        self.drawing_tracker = DrawingTracker(
            width=rect.width,
            height=rect.height,
            config=drawing_config
        )
    
    def update(self, frame: Optional[Union[np.ndarray, float]] = None) -> None:
        """Update canvas state with new frame.
        
        Args:
            frame: New frame to display (raw camera frame)
        """
        if frame is None:
            self.logger.warning("Received None frame")
            return
            
        try:
            if isinstance(frame, np.ndarray):
                # self.logger.info(f"Received frame: shape={frame.shape}, dtype={frame.dtype}")
                
                # Ensure frame has correct dimensions and type
                if frame.shape[1] != self.rect.width or frame.shape[0] != self.rect.height:
                    self.logger.info(f"Resizing frame from {frame.shape[:2]} to {(self.rect.height, self.rect.width)}")
                    frame = cv2.resize(frame, (self.rect.width, self.rect.height))
                
                if frame.dtype != np.uint8:
                    self.logger.info(f"Converting frame from {frame.dtype} to uint8")
                    frame = frame.astype(np.uint8)
                
                # # Check if frame contains any data
                # if frame.size == 0 or frame.mean() == 0:
                #     self.logger.warning("Frame appears to be empty or black")
                # else:
                #     self.logger.info(f"Frame mean pixel value: {frame.mean():.2f}")
                    
                # Store raw camera frame
                self.current_frame = frame.copy()
            else:
                self.logger.warning(f"Invalid frame type received: {type(frame)}")
        except Exception as e:
            self.logger.error(f"Error updating frame: {e}")
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the canvas contents to screen."""
        if not self.visible:
            return
            
        try:
            # Use blank frame if no camera feed
            display_frame = self.current_frame if self.current_frame is not None else self.blank_frame
            
            if display_frame is None:
                pygame.draw.rect(screen, Colors.RED, self.rect, 2)
                return
                
            # Convert frame to pygame surface
            display = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            display_surface = pygame.surfarray.make_surface(display.swapaxes(0, 1))
            
            # Draw camera frame
            screen.blit(display_surface, self.rect)
            
            # Draw trail with improved visuals
            self._draw_trail_points(screen)
            
            # Draw border
            pygame.draw.rect(screen, Colors.BORDER, self.rect, 2)
        
        except Exception as e:
            self.logger.error(f"Error drawing frame: {e}")
            pygame.draw.rect(screen, Colors.RED, self.rect, 2)
    
    def _draw_trail_points(self, screen: pygame.Surface) -> None:
        """Draw the trail points on the screen."""
        trail_points = self.drawing_tracker.get_trail_points()
        # self.logger.info(f"Drawing trail points: count={len(trail_points)}")
        if len(trail_points) > 1:
            # Offset points by canvas position
            adjusted_points = [(x + self.rect.x, y + self.rect.y) 
                             for x, y in trail_points]
            pygame.draw.lines(
                screen,
                Colors.TRAIL_COLOR,
                False,
                adjusted_points,
                8  # Thickness parameter
            )
            self.logger.info(f"Drew lines with {len(adjusted_points)} points")
    
    def update_hand_position(self, hand_point: Optional[HandPoint]) -> None:
        """Update hand position and drawing state.
        
        Args:
            hand_point: Current hand position
        """
        # Convert normalized coordinates to canvas coordinates
        x = int(hand_point.x * self.rect.width)
        y = int(hand_point.y * self.rect.height)
        
        # Update drawing tracker
        smoothed_pos = self.drawing_tracker.update(
            position=(x, y),
            is_drawing=self.is_drawing
        )
        
        if smoothed_pos:
            self.last_position = smoothed_pos
            
            if self.is_drawing:
                metrics = self.drawing_tracker.get_drawing_metrics()
                self.logger.debug(f"Drawing metrics: {metrics}")
    
    def set_drawing_state(self, is_drawing: bool) -> None:
        """Set whether currently drawing.
        
        Args:
            is_drawing: Whether drawing is enabled
        """
        self.logger.info(f"Setting drawing state to: {is_drawing}")
        if self.is_drawing != is_drawing:
            self.is_drawing = is_drawing
    
    def get_drawing_state(self) -> bool:
        """Get current drawing state.
        
        Returns:
            bool: Whether drawing is enabled
        """
        return self.is_drawing
        
    def clear(self) -> None:
        """Reset the canvas display state."""
        self.current_frame = None
        self.last_position = None
        self.drawing_tracker.clear()
