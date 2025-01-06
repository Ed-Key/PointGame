# ui/base.py
from abc import ABC, abstractmethod
import pygame

class UIComponent(ABC):
    """Abstract base class for UI components."""
    
    def __init__(self, rect: pygame.Rect):
        """Initialize the UI component.
        
        Args:
            rect: The component's position and size
        """
        self.rect = rect
        self.visible = True
        
    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the component on the screen.
        
        Args:
            screen: Pygame surface to draw on
        """
        pass
        
    @abstractmethod
    def update(self, *args, **kwargs) -> None:
        """Update the component's state."""
        pass
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle an event.
        
        Args:
            event: Pygame event to handle
            
        Returns:
            bool: True if event was handled, False otherwise
        """
        return False
        
    def show(self) -> None:
        """Make the component visible."""
        self.visible = True
        
    def hide(self) -> None:
        """Make the component invisible."""
        self.visible = False