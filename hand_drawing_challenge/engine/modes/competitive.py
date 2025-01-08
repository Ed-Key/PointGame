# hand_drawing_challenge/engine/modes/competitive.py

import pygame
from typing import Any
from .base_mode import GameMode
from ...events.bus import EventBus
from ...events.types import GameEventType

class CompetitiveMode(GameMode):
    """Placeholder implementation for competitive mode."""
    
    def __init__(self, event_bus: EventBus):
        super().__init__(event_bus)
        self.font = None
        
    def initialize(self) -> None:
        """Initialize mode-specific resources."""
        self.font = pygame.font.Font(None, 48)
    
    def update(self, delta_time: float) -> None:
        """Update game state."""
        if not self.is_active:
            return
            
        # Draw placeholder screen
        screen = pygame.display.get_surface()
        if screen:
            screen.fill((0, 0, 100))  # Dark blue background to distinguish from single player
            
            # Draw mode indicator
            text = self.font.render("Competitive Mode", True, (255, 255, 255))
            text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
            screen.blit(text, text_rect)
            
            # Draw instruction
            instruction = self.font.render("Press ESC to return to menu", True, (200, 200, 200))
            inst_rect = instruction.get_rect(centerx=screen.get_width() // 2, bottom=screen.get_height() - 50)
            screen.blit(instruction, inst_rect)
    
    def handle_input(self, event: Any) -> None:
        """Handle input events."""
        if isinstance(event, pygame.event.Event):
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Return to menu
                    self.event_bus.publish(GameEventType.GAME_ENDED)
                    self.stop()