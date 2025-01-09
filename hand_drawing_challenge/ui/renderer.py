import pygame
from typing import Optional, Tuple

class Renderer:
    """
    Handles the actual rendering of UI components to the screen.
    
    Responsibilities:
    - Manages the pygame window and display
    - Provides drawing utilities
    - Handles basic screen operations (clear, present)
    """
    
    def __init__(self, screen_size: Tuple[int, int]):
        """
        Initialize the renderer.
        
        Args:
            screen_size: Tuple of (width, height) for window
        """
        pygame.init()
        self.screen_size = screen_size
        self.screen = pygame.display.set_mode(screen_size)
        pygame.display.set_caption("Hand Drawing Challenge")
        
        # Background color (black)
        self.bg_color = (0, 0, 0)
    
    def clear(self) -> None:
        """Clear the screen with background color."""
        self.screen.fill(self.bg_color)
    
    def present(self) -> None:
        """Update the display with rendered content."""
        pygame.display.flip()
    
    def get_screen(self) -> pygame.Surface:
        """
        Get the pygame screen surface.
        
        Returns:
            pygame.Surface: The main screen surface
        """
        return self.screen
    
    def cleanup(self) -> None:
        """Clean up renderer resources."""
        # Clear references
        self.screen = None
        self.screen_size = None
