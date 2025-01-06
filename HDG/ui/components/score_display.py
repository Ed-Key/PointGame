# ui/components/score_display.py
import pygame
from typing import List, Tuple
from ..base import UIComponent
from ..utils.colors import Colors

class ScoreDisplay(UIComponent):
    """Component for displaying game stats and score."""
    
    def __init__(self, rect: pygame.Rect):
        """Initialize the score display.
        
        Args:
            rect: Position and size of the display
        """
        super().__init__(rect)
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 36)
        self.score = 0
        self.game_state = "waiting"
        self.is_drawing = False
    
    def update(self, score: int = None, game_state: str = None, 
               is_drawing: bool = None) -> None:
        """Update the display stats.
        
        Args:
            score: Current score
            game_state: Current game state
            is_drawing: Whether currently drawing
        """
        if score is not None:
            self.score = score
        if game_state is not None:
            self.game_state = game_state
        if is_drawing is not None:
            self.is_drawing = is_drawing
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the score display.
        
        Args:
            screen: Pygame surface to draw on
        """
        if not self.visible:
            return
            
        # Draw border and background
        pygame.draw.rect(screen, Colors.BORDER, self.rect, 2)
        
        # Draw title
        title = self.title_font.render("Game Stats", True, Colors.TEXT)
        title_rect = title.get_rect(
            centerx=self.rect.centerx,
            top=self.rect.top - 40
        )
        screen.blit(title, title_rect)
        
        # Draw stats
        stats = [
            f"Score: {self.score}",
            f"Status: {self.game_state}",
            f"Drawing: {'Yes' if self.is_drawing else 'No'}"
        ]
        
        y_offset = self.rect.top + 30
        for stat in stats:
            text = self.font.render(stat, True, Colors.TEXT)
            screen.blit(text, (self.rect.left + 20, y_offset))
            y_offset += 50