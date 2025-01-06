# ui/base.py
import pygame

class UIComponent:
    """Base class for UI components."""
    
    def __init__(self, event_bus, rect: pygame.Rect = None):
        """Initialize the UI component.
        
        Args:
            event_bus: Event bus for component communication
            rect: Position and size of the component
        """
        self._event_bus = event_bus
        self.rect = rect
        self.visible = True
    
    def update(self, *args, **kwargs) -> None:
        """Update component state. To be implemented by subclasses."""
        pass
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw component to screen. To be implemented by subclasses.
        
        Args:
            screen: Pygame surface to draw on
        """
        pass
