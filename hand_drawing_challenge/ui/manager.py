# hand_drawing_challenge/ui/manager.py

from typing import Dict, Optional
import pygame
import numpy as np
import logging
from ..events.bus import EventBus
from ..events.types import GameEventType
from .base import UIComponent
from .renderer import Renderer
from ..input.manager import InputManager
from .components.canvas import DrawingCanvas
from .components.pattern_display import PatternDisplay
from .components.score_display import ScoreDisplay

class UIManager:
    """
    Manages all UI components and coordinates with the renderer.
    """

    def __init__(self, event_bus: EventBus, screen_size: tuple[int, int] = (1280, 720)):
        """Initialize the UI manager."""
        print(">>> ui/manager.py: UIManager.__init__() called")
        self.event_bus = event_bus
        self.screen_size = screen_size
        self.components: Dict[str, UIComponent] = {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize renderer
        self.renderer = Renderer(screen_size)
        
        # Initialize input manager with same event bus
        print(">>> ui/manager.py: Creating InputManager...")
        self.input_manager = InputManager(self.event_bus, camera_id=0)
        
        # Last valid frame
        self.current_frame: Optional[np.ndarray] = None

        # Subscribe to relevant events
        self.event_bus.subscribe(GameEventType.GAME_ENDED, self._handle_game_end)
        self.event_bus.subscribe(GameEventType.MENU_BACK, self._handle_menu_back)
        self.event_bus.subscribe(GameEventType.HAND_POSITION_UPDATED, self._handle_hand_position)

        # Initialize UI components
        self._init_components()

    def _init_components(self) -> None:
        """Initialize and position all UI components."""
        # Main drawing area (center)
        self.components['canvas'] = DrawingCanvas(
            pygame.Rect(320, 120, 640, 480)
        )

        # Pattern display (left)
        self.components['pattern'] = PatternDisplay(
            pygame.Rect(20, 120, 280, 280)
        )

        # Score display (right)
        self.components['score'] = ScoreDisplay(
            pygame.Rect(980, 120, 280, 480)
        )

    def update(self, delta_time: float, score: int = 0, game_state: str = "Ready", is_drawing: bool = False) -> None:
        """Update all UI components."""
        try:
            # Process input
            self.input_manager.process_input()
            
            # Get latest frame
            frame = self.input_manager.get_frame()
            if isinstance(frame, np.ndarray):
                self.current_frame = frame
                # Update drawing canvas with new frame
                canvas = self.get_component('canvas')
                if canvas and isinstance(canvas, DrawingCanvas):
                    canvas.update(frame)

            # Update other components
            for component in self.components.values():
                if not component.visible:
                    continue

                # Update specific component types
                if isinstance(component, ScoreDisplay):
                    component.update(score, game_state, is_drawing)
                elif not isinstance(component, DrawingCanvas):  # Skip DrawingCanvas as it's handled above
                    component.update(delta_time)

        except Exception as e:
            self.logger.error(f"Error updating UI components: {e}")

    def render(self) -> None:
        """Render all UI components using the renderer."""
        # Clear screen
        self.renderer.clear()

        # Render each visible component
        for component in self.components.values():
            if component.visible:
                component.draw(self.renderer.get_screen())

        # Update display
        self.renderer.present()

    def get_component(self, name: str) -> Optional[UIComponent]:
        """Get a UI component by name."""
        return self.components.get(name)

    def set_component_visibility(self, name: str, visible: bool) -> None:
        """Set visibility of a UI component."""
        if name in self.components:
            self.components[name].visible = visible

    def update_frame(self, frame: Optional[np.ndarray]) -> None:
        """Update components with new frame data."""
        if frame is not None and isinstance(frame, np.ndarray):
            self.current_frame = frame
            canvas = self.get_component('canvas')
            if canvas and isinstance(canvas, DrawingCanvas):
                canvas.update(frame)

    def clear_canvas(self) -> None:
        """Clear the drawing canvas."""
        canvas = self.get_component('canvas')
        if canvas and isinstance(canvas, DrawingCanvas):
            canvas.clear()

    def _handle_game_end(self, event_type: GameEventType, data: Optional[dict] = None) -> None:
        """Handle cleanup on game end."""
        self.stop_input_processing()
        self.renderer.cleanup()
        self.input_manager.cleanup()

    def _handle_menu_back(self, event_type: GameEventType, data: Optional[dict] = None) -> None:
        """Handle returning to menu."""
        self.stop_input_processing()

    def _handle_hand_position(self, event_type: GameEventType, data: Optional[dict] = None) -> None:
        """Handle hand position updates."""
        if data and "position" in data:
            canvas = self.get_component('canvas')
            if canvas and isinstance(canvas, DrawingCanvas):
                canvas.update_hand_position(data["position"])

    def cleanup(self) -> None:
        """Clean up all resources."""
        try:
            # First unsubscribe from all events
            if hasattr(self, 'event_bus'):
                self.event_bus.unsubscribe(GameEventType.GAME_ENDED, self._handle_game_end)
                self.event_bus.unsubscribe(GameEventType.MENU_BACK, self._handle_menu_back)
                self.event_bus.unsubscribe(GameEventType.HAND_POSITION_UPDATED, self._handle_hand_position)
            
            # Then cleanup components in order
            if hasattr(self, 'input_manager'):
                self.input_manager.cleanup()
                
            if hasattr(self, 'renderer'):
                self.renderer.cleanup()
                
            self.components.clear()
            
            # Finally null event bus reference
            if hasattr(self, 'event_bus'):
                self.event_bus = None
                
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    def start_input_processing(self) -> None:
        """Start input processing."""
        print(">>> ui/manager.py: start_input_processing() called")
        if hasattr(self, 'input_manager'):
            print(">>> ui/manager.py: Calling input_manager.start()")
            self.input_manager.start()
        else:
            print(">>> ui/manager.py: WARNING - No input_manager found!")

    def stop_input_processing(self) -> None:
        """Stop input processing."""
        if hasattr(self, 'input_manager'):
            self.input_manager.stop()
