# hand_drawing_challenge/ui/components/canvas.py

import cv2
import numpy as np
import pygame
from typing import Optional, Tuple
from ..base import UIComponent
from ..utils.colors import Colors
from ...events.bus import EventBus
from ...input.drawing_tracker import DrawingTracker

class DrawingCanvas(UIComponent):
    """Drawing canvas component that displays camera feed and drawing visualization."""
    
    def __init__(self, event_bus: EventBus, rect: pygame.Rect):
        """Initialize drawing canvas.
        
        Args:
            event_bus: Event bus for component communication
            rect: Position and size of the canvas
        """
        super().__init__(event_bus, rect)
        self.canvas = np.zeros((rect.height, rect.width, 3), dtype=np.uint8)
        self.drawing_tracker = DrawingTracker(width=rect.width, height=rect.height)
        self.is_drawing = False
        self.current_frame = None
        self.last_position: Optional[Tuple[int, int]] = None

    def update(self, frame: Optional[np.ndarray] = None) -> None:
        """Update canvas state with new frame.
        
        Args:
            frame: New camera frame to display
        """
        if frame is not None and isinstance(frame, np.ndarray):
            self.current_frame = frame.copy()

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the canvas with camera feed and drawing overlay."""
        if not self.visible:
            pygame.draw.rect(screen, Colors.BACKGROUND, self.rect)
            pygame.draw.rect(screen, Colors.BORDER, self.rect, 2)
            return

        if self.current_frame is not None:
            # Combine camera frame and drawing canvas
            display = cv2.addWeighted(
                self.current_frame, 
                1.0,
                self.canvas,
                0.7,
                0
            )

            # Convert to pygame surface
            display = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
            display_surface = pygame.surfarray.make_surface(display)
            
            # Handle rotation if needed
            display_surface = pygame.transform.rotate(display_surface, 270)
            
            # Draw to screen
            screen.blit(display_surface, self.rect)
        
        pygame.draw.rect(screen, Colors.BORDER, self.rect, 2)

    def clear(self) -> None:
        """Clear the drawing canvas and reset state."""
        self.canvas.fill(0)
        self.drawing_tracker.clear()
        self.last_position = None

    def set_drawing_state(self, is_drawing: bool) -> None:
        """Set drawing state."""
        self.is_drawing = is_drawing

# hand_drawing_challenge/ui/components/score_display.py

import pygame
from typing import Optional
from ..base import UIComponent
from ..utils.colors import Colors
from ...events.bus import EventBus
from ...events.types import GameEventType

class ScoreDisplay(UIComponent):
    """Component for displaying score and game state."""
    
    def __init__(self, event_bus: EventBus, rect: pygame.Rect):
        """Initialize score display.
        
        Args:
            event_bus: Event bus for component communication
            rect: Position and size of the display
        """
        super().__init__(event_bus, rect)
        self.score = 0
        self.game_state = "Ready"
        self.is_drawing = False
        self.font = pygame.font.Font(None, 36)
        
        # Subscribe to score events
        self._event_bus.subscribe(GameEventType.SCORE_UPDATED, self._handle_score_update)
    
    def _handle_score_update(self, event_type: GameEventType, data: Optional[dict]) -> None:
        """Handle score update events."""
        if data and 'score' in data:
            self.score = data['score']
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the score display."""
        if not self.visible:
            return
            
        pygame.draw.rect(screen, Colors.COMPONENT_BG, self.rect)
        pygame.draw.rect(screen, Colors.BORDER, self.rect, 2)
        
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, Colors.TEXT)
        score_rect = score_text.get_rect(centerx=self.rect.centerx, top=self.rect.top + 20)
        screen.blit(score_text, score_rect)
        
        # Draw state
        state_color = Colors.SUCCESS if self.is_drawing else Colors.TEXT
        state_text = self.font.render(self.game_state, True, state_color)
        state_rect = state_text.get_rect(centerx=self.rect.centerx, top=score_rect.bottom + 20)
        screen.blit(state_text, state_rect)
