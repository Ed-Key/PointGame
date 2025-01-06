# ui/components/canvas.py
import cv2
import numpy as np
import pygame
from typing import Optional, Tuple
from ..base import UIComponent
from ..utils.colors import Colors
from hand_drawing_challenge.input.drawing_tracker import DrawingTracker
from hand_drawing_challenge.input.processors.hand_tracking import HandPoint

class DrawingCanvas(UIComponent):
    """
    Drawing canvas component that displays camera feed and handles drawing visualization.

    This component:
    - Shows live camera feed as background
    - Overlays drawing trails
    - Provides visual feedback for hand tracking
    - Handles drawing state and trail management
    """

    def __init__(self, rect: pygame.Rect):
        """Initialize the drawing canvas.

        Args:
            rect: Position and size of the canvas
        """
        super().__init__(rect)
        # Drawing surface for trails
        self.canvas = np.zeros((rect.height, rect.width, 3), dtype=np.uint8)

        # Initialize drawing tracker with canvas dimensions
        self.drawing_tracker = DrawingTracker(
            width=rect.width,
            height=rect.height
        )

        # State
        self.is_drawing = False
        self.current_frame = None
        self.last_position: Optional[Tuple[int, int]] = None


    def update(self, *args, **kwargs) -> None:
        """Update canvas state.

        Can handle either:
        - delta_time: Time elapsed since last update
        - processed_frame: New frame to display
        """
        # If first arg is a numpy array, treat as frame
        if args and isinstance(args[0], np.ndarray):
            self.current_frame = args[0].copy()

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the canvas with camera feed and drawing overlay.

        Args:
            screen: Pygame surface to draw on
        """
        if not self.visible or self.current_frame is None:
            # Draw placeholder if no camera feed
            pygame.draw.rect(screen, Colors.BACKGROUND, self.rect)
            pygame.draw.rect(screen, Colors.BORDER, self.rect, 2)
            return

        # Combine camera frame and drawing canvas
        display = cv2.addWeighted(
            self.current_frame,
            1.0,  # Camera frame weight
            self.canvas,
            0.7,  # Drawing trail weight
            0
        )

        # Convert to pygame surface
        display = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
        display_surface = pygame.surfarray.make_surface(display)

        # Rotate if needed (depending on camera orientation)
        display_surface = pygame.transform.rotate(display_surface, 270)

        # Draw to screen
        screen.blit(display_surface, self.rect)
        pygame.draw.rect(screen, Colors.BORDER, self.rect, 2)

    def clear(self) -> None:
        """Clear the drawing canvas and reset trail."""
        self.canvas.fill(0)
        self.drawing_tracker.clear()
        self.last_position = None

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

    def get_last_position(self) -> Optional[Tuple[int, int]]:
        """Get the last known hand position.

        Returns:
            Tuple[int, int] or None: Last (x, y) position if available
        """
        return self.last_position

