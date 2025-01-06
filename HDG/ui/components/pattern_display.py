# ui/components/pattern_display.py
import pygame
from ..base import UIComponent
from ..utils.colors import Colors

class PatternDisplay(UIComponent):
    """Component for displaying the target pattern to draw."""
    
    def __init__(self, rect: pygame.Rect):
        """Initialize the pattern display.
        
        Args:
            rect: Position and size of the display
        """
        super().__init__(rect)
        self.pattern_surface = None
        self.title_font = pygame.font.Font(None, 36)
    
    def update(self, pattern_surface: pygame.Surface = None) -> None:
        """Update the pattern to display.
        
        Args:
            pattern_surface: New pattern to display
        """
        self.pattern_surface = pattern_surface
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the pattern display.
        
        Args:
            screen: Pygame surface to draw on
        """
        if not self.visible:
            return
            
        # Draw border
        pygame.draw.rect(screen, Colors.BORDER, self.rect, 2)
        
        # Draw title
        title = self.title_font.render("Pattern to Draw", True, Colors.TEXT)
        title_rect = title.get_rect(
            centerx=self.rect.centerx,
            top=self.rect.top - 40
        )
        screen.blit(title, title_rect)
        
        # Draw pattern if available
        if self.pattern_surface:
            pattern_rect = self.pattern_surface.get_rect(center=self.rect.center)
            screen.blit(self.pattern_surface, pattern_rect)