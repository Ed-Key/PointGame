# hand_drawing_challenge/ui/manager.py

from typing import Dict, Optional, Tuple
import pygame
import numpy as np
from ..events.bus import EventBus
from ..events.types import GameEventType
from .base import UIComponent
from .renderer import Renderer
from .components.canvas import DrawingCanvas
from .components.pattern_display import PatternDisplay
from .components.score_display import ScoreDisplay

class UIManager:
    """
    Manages all UI components and coordinates with the renderer.
    """
    
    def __init__(self, event_bus: EventBus, screen_size: Tuple[int, int] = (1280, 720)):
        """Initialize the UI manager.
        
        Args:
            event_bus: Central event bus for game events
            screen_size: Tuple of (width, height) for the game window
        """
        self.event_bus = event_bus
        self.screen_size = screen_size
        self.components: Dict[str, UIComponent] = {}
        
        # Initialize renderer
        self.renderer = Renderer(screen_size)
        
        # Subscribe to relevant events
        self.event_bus.subscribe(GameEventType.GAME_ENDED, self._handle_game_end)
        
        # Initialize UI components
        self._init_components()
    
    def _init_components(self) -> None:
        """Initialize and position all UI components."""
        # Main drawing area (center)
        self.components['canvas'] = DrawingCanvas(
            self.event_bus,
            pygame.Rect(320, 120, 640, 480)
        )
        
        # Pattern display (left)
        self.components['pattern'] = PatternDisplay(
            self.event_bus,
            pygame.Rect(20, 120, 280, 280)
        )
        
        # Score display (right)
        self.components['score'] = ScoreDisplay(
            self.event_bus,
            pygame.Rect(980, 120, 280, 480)
        )
    
    def update(self, delta_time: float) -> None:
        """Update all UI components.
        
        Args:
            delta_time: Time elapsed since last update
        """
        for component in self.components.values():
            if not component.visible:
                continue
                
            if isinstance(component, ScoreDisplay):
                # Score display has different update parameters
                component.update(
                    score=0,  # TODO: Track actual score
                    game_state="Ready",  # Default state
                    is_drawing=False  # Default not drawing
                )
            else:
                component.update(delta_time)
    
    def render(self) -> None:
        """Render all visible UI components."""
        # Clear screen
        self.renderer.clear()
        
        # Render each visible component
        screen = self.renderer.get_screen()
        for component in self.components.values():
            if component.visible:
                component.draw(screen)
        
        # Update display
        self.renderer.present()
    
    def get_component(self, name: str) -> Optional[UIComponent]:
        """Get a UI component by name.
        
        Args:
            name: Name of the component to retrieve
            
        Returns:
            UIComponent if found, None otherwise
        """
        return self.components.get(name)
    
    def set_component_visibility(self, name: str, visible: bool) -> None:
        """Set visibility of a UI component.
        
        Args:
            name: Name of the component
            visible: Whether component should be visible
        """
        if name in self.components:
            self.components[name].visible = visible
    
    def update_frame(self, frame: np.ndarray) -> None:
        """Update drawing canvas with new frame data.
        
        Args:
            frame: New camera frame to display
        """
        canvas = self.get_component('canvas')
        if canvas and isinstance(canvas, DrawingCanvas):
            canvas.update(frame)
    
    def _handle_game_end(self, event_type: GameEventType, data: Optional[dict] = None) -> None:
        """Handle cleanup on game end."""
        self.renderer.cleanup()
