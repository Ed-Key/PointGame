# hand_drawing_challenge/engine/modes/single_player.py

import logging
import pygame
from typing import Optional
from ...events.bus import EventBus
from ...events.types import GameEventType
from ...services.pattern_manager import PatternManager
from ...ui.manager import UIManager
from .base_mode import GameMode

class SinglePlayerMode(GameMode):
    """Single player game mode implementation."""
    
    def __init__(self, event_bus: EventBus, ui_manager: UIManager):
        """Initialize single player mode."""
        print(">>> single_player.py: SinglePlayerMode.__init__() called")
        print(f">>> single_player.py: SinglePlayerMode, ui_manager = {ui_manager}")
        print(">>> single_player.py: SinglePlayerMode, ui_manager.input_manager =", ui_manager.input_manager)


        super().__init__(event_bus)
        self.ui_manager = ui_manager
        self.logger = logging.getLogger(__name__)
        self.pattern_manager = PatternManager(event_bus)
        
        # Game state
        self.current_pattern = None
        self.is_drawing = False
        self.score = 0
        self.round_count = 0
        self.max_rounds = 5
        
        # Get component references
        self.canvas = None
        
    def initialize(self) -> None:
        """Initialize the single player mode."""
        try:
            self.logger.info("Initializing single player mode")
            super().initialize()
            
            # Initialize pattern manager and get first pattern
            self.pattern_manager.initialize()
            self.current_pattern = self.pattern_manager.get_next_pattern()
            
            # Get UI component references
            self.canvas = self.ui_manager.get_component('canvas')
            if not self.canvas:
                raise RuntimeError("Required UI components not found")
            
            # Reset game state
            self.score = 0
            self.round_count = 0
            self.is_drawing = False
            
            # Clear canvas
            self.canvas.clear()
            
        except Exception as e:
            self.logger.error(f"Error initializing single player mode: {e}")
            raise
    
    def update(self, delta_time: float) -> None:
        """Update game state."""
        if not self.is_active:
            return
            
        try:
            # Update UI components through UIManager
            self.ui_manager.update(
                delta_time=delta_time,
                score=self.score,
                game_state="Drawing" if self.is_drawing else "Ready",
                is_drawing=self.is_drawing
            )
            
        except Exception as e:
            self.logger.error(f"Error updating single player mode: {e}")
    
    def handle_input(self, event: pygame.event.Event) -> None:
        """Handle input events."""
        try:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.ui_manager.stop_input_processing()
                    self.event_bus.publish(GameEventType.MENU_BACK) 
                elif event.key == pygame.K_SPACE:
                    self._toggle_drawing()
                elif event.key == pygame.K_c:
                    self._clear_canvas()
                    
        except Exception as e:
            self.logger.error(f"Error handling input: {e}")
    
    def _toggle_drawing(self) -> None:
        """Toggle drawing state."""
        try:
            if self.canvas:
                self.is_drawing = not self.is_drawing
                self.canvas.set_drawing_state(self.is_drawing)
                
                # Update hand tracking processor drawing state
                hand_tracker = self.ui_manager.input_manager.get_processor("hand_tracking")
                if hand_tracker:
                    hand_tracker.set_drawing_state(self.is_drawing)
                
                # Publish appropriate event
                event_type = GameEventType.DRAWING_STARTED if self.is_drawing else GameEventType.DRAWING_ENDED
                self.event_bus.publish(event_type)
        except Exception as e:
            self.logger.error(f"Error toggling drawing state: {e}")
    
    def _clear_canvas(self) -> None:
        """Clear the drawing canvas."""
        if self.canvas:
            self.canvas.clear()
    
    def start(self) -> None:
        """Start the game mode."""
        try:
            super().start()
            self.logger.info("Starting single player mode")
        
            # Start input processing
            if self.ui_manager:
                self.logger.info("Starting input processing for single player mode")
                self.ui_manager.start_input_processing()
            
        except Exception as e:
            self.logger.error(f"Error starting single player mode: {e}")
            raise
    
    def stop(self) -> None:
        """Stop the game mode."""
        self.logger.info("Stopping single player mode")
        
        if self.ui_manager:
            self.ui_manager.stop_input_processing()
        
        super().stop()
