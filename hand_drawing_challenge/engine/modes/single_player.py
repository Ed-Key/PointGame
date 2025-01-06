# engine/modes/single_player.py
from typing import Optional
import pygame
from .base_mode import GameMode
from ...services.pattern_manager import PatternManager
from ...events.bus import EventBus
from ...events.events import PatternGeneratedEvent, PatternCompletedEvent
from ...ui.components.pattern_display import PatternDisplay
from ...ui.components.canvas import DrawingCanvas
from ...ui.components.score_display import ScoreDisplay

class SinglePlayerMode(GameMode):
    def __init__(self, event_bus: EventBus):
        super().__init__(event_bus)
        self.pattern_manager = PatternManager(event_bus)
        self.current_pattern = None
        
        # Define component layout
        window_width = 800
        window_height = 600
        pattern_height = 200
        score_height = 100
        canvas_height = window_height - pattern_height - score_height
        
        # Create rects for UI components
        pattern_rect = pygame.Rect(0, 0, window_width, pattern_height)
        canvas_rect = pygame.Rect(0, pattern_height, window_width, canvas_height)
        score_rect = pygame.Rect(0, pattern_height + canvas_height, window_width, score_height)
        
        # Initialize UI components with proper rects
        self.pattern_display = PatternDisplay(event_bus, pattern_rect)
        self.drawing_canvas = DrawingCanvas(event_bus, canvas_rect)
        self.score_display = ScoreDisplay(event_bus, score_rect)
        
        # Subscribe to pattern events
        self.event_bus.subscribe(PatternGeneratedEvent, self._on_pattern_generated)
        self.event_bus.subscribe(PatternCompletedEvent, self._on_pattern_completed)

    def initialize(self) -> None:
        """Initialize the single player mode"""
        super().initialize()
        self.pattern_manager.initialize()
        # Get first pattern - this will trigger PatternGeneratedEvent
        self.pattern_manager.get_next_pattern()

    def update(self, dt: float) -> None:
        """Update game state"""
        super().update(dt)
        self.pattern_display.update(dt)
        self.drawing_canvas.update(dt)
        # Pass required arguments to score display
        self.score_display.update(
            score=0,  # TODO: Track actual score
            game_state="Drawing" if self.drawing_canvas.is_drawing else "Ready",
            is_drawing=self.drawing_canvas.is_drawing
        )

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the current game state"""
        self.pattern_display.draw(screen)
        self.drawing_canvas.draw(screen)
        self.score_display.draw(screen)

    def _on_pattern_generated(self, event: PatternGeneratedEvent) -> None:
        """Handle pattern generated event"""
        self.current_pattern = event.pattern
        print(f"New pattern generated: {event.pattern.name}")
        # The pattern display component should also be subscribed to this event
        # to update its display

    def _on_pattern_completed(self, event: PatternCompletedEvent) -> None:
        """Handle pattern completed event"""
        print(f"Pattern completed with score: {event.score}")
        # The score display component should be subscribed to this event
        # to update the score
        
    def handle_input(self, event: pygame.event.Event) -> None:
        """Handle input events.
        
        Args:
            event: Pygame event to process
        """
        # Delegate input handling to the drawing canvas
        self.drawing_canvas.handle_input(event)
