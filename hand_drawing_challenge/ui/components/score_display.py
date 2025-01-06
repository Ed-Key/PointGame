# ui/components/score_display.py
import pygame
from ..base import UIComponent
from ..utils.colors import Colors

class ScoreDisplay(UIComponent):
    """Component for displaying the current score and game state."""
    
    def __init__(self, event_bus, rect: pygame.Rect):
        super().__init__(rect)
        self.event_bus = event_bus
        self.score = 0
        self.game_state = "Ready"
        self.is_drawing = False
        self.font = pygame.font.Font(None, 36)
        
    def update(self, score: int, game_state: str, is_drawing: bool) -> None:
        """Update the display state."""
        self.score = score
        self.game_state = game_state
        self.is_drawing = is_drawing
        
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the score display component."""
        # Draw background
        pygame.draw.rect(screen, Colors.COMPONENT_BG, self.rect)
        pygame.draw.rect(screen, Colors.BORDER, self.rect, 2)
        
        # Draw title
        title = self.font.render("Score", True, Colors.TEXT)
        title_rect = title.get_rect(centerx=self.rect.centerx, top=self.rect.top + 10)
        screen.blit(title, title_rect)
        
        # Draw score
        score_text = self.font.render(str(self.score), True, Colors.TEXT)
        score_rect = score_text.get_rect(centerx=self.rect.centerx, top=title_rect.bottom + 20)
        screen.blit(score_text, score_rect)
        
        # Draw game state
        state_color = Colors.SUCCESS if self.is_drawing else Colors.TEXT
        state_text = self.font.render(self.game_state, True, state_color)
        state_rect = state_text.get_rect(centerx=self.rect.centerx, top=score_rect.bottom + 40)
        screen.blit(state_text, state_rect)
