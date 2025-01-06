# ui/components/pattern_display.py
import pygame
from ..base import UIComponent
from ..utils.colors import Colors

class PatternDisplay(UIComponent):
    """Component for displaying the pattern to be drawn."""

    def __init__(self, rect: pygame.Rect):
        super().__init__(rect)
        self.current_pattern = None
        self.font = pygame.font.Font(None, 36)

    def set_pattern(self, pattern) -> None:
        """Set the current pattern to display."""
        self.current_pattern = pattern

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the pattern display component."""
        # Draw background
        pygame.draw.rect(screen, Colors.COMPONENT_BG, self.rect)
        pygame.draw.rect(screen, Colors.BORDER, self.rect, 2)

        # Draw title
        title = self.font.render("Pattern", True, Colors.TEXT)
        title_rect = title.get_rect(centerx=self.rect.centerx, top=self.rect.top + 10)
        screen.blit(title, title_rect)

        if self.current_pattern:
            # Draw the actual pattern (placeholder)
            pattern_rect = pygame.Rect(
                self.rect.x + 20,
                self.rect.y + 60,
                self.rect.width - 40,
                self.rect.height - 80
            )
            pygame.draw.rect(screen, Colors.PATTERN, pattern_rect)
        else:
            # Draw "No Pattern" text
            text = self.font.render("No Pattern", True, Colors.TEXT)
            text_rect = text.get_rect(center=self.rect.center)
            screen.blit(text, text_rect)

