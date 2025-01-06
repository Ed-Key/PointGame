# ui/base.py
import pygame

class UIComponent:
    """Base class for UI components."""

    def __init__(self, rect: pygame.Rect):
        """Initialize the UI component.

        Args:
            rect: Position and size of the component
        """
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

