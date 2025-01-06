# hand_drawing_challenge/engine/modes/menu_mode.py

import pygame
from typing import Any
from .base_mode import GameMode
from ...events.bus import EventBus
from ...events.types import GameEventType

class MenuMode(GameMode):
    """Menu mode implementation that follows the GameMode interface."""
    
    def __init__(self, event_bus: EventBus):
        """Initialize menu mode."""
        super().__init__(event_bus)
        self.font_large = None
        self.font_normal = None
        
        # Button rectangles for collision detection
        self.single_player_rect = pygame.Rect(0, 0, 300, 60)
        self.competitive_rect = pygame.Rect(0, 0, 300, 60)
        self.buttons_initialized = False
    
    def initialize(self) -> None:
        """Initialize mode-specific resources and state."""
        self.font_large = pygame.font.Font(None, 74)
        self.font_normal = pygame.font.Font(None, 48)
        
        if not self.buttons_initialized:
            # Center the buttons
            screen_rect = pygame.display.get_surface().get_rect()
            center_x = screen_rect.centerx
            center_y = screen_rect.centery
            
            # Position buttons
            self.single_player_rect.centerx = center_x
            self.single_player_rect.centery = center_y - 40
            
            self.competitive_rect.centerx = center_x
            self.competitive_rect.centery = center_y + 40
            
            self.buttons_initialized = True
    
    def update(self, delta_time: float) -> None:
        """Update menu state and handle input.
        
        Args:
            delta_time: Time elapsed since last update in seconds
        """
        if not self.is_active:
            return
        
        # Draw menu (in actual implementation, this should be handled by UI system)
        screen = pygame.display.get_surface()
        if screen:
            self._draw(screen)
    
    def handle_input(self, event: Any) -> None:
        """Handle input events.
        
        Args:
            event: Input event to process
        """
        if not isinstance(event, pygame.event.Event):
            return
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if self.single_player_rect.collidepoint(mouse_pos):
                self.event_bus.publish(GameEventType.GAME_MODE_SELECTED, {"mode": "single_player"})
            elif self.competitive_rect.collidepoint(mouse_pos):
                self.event_bus.publish(GameEventType.GAME_MODE_SELECTED, {"mode": "competitive"})
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.event_bus.publish(GameEventType.GAME_ENDED)
    
    def _draw(self, screen: pygame.Surface) -> None:
        """Draw the menu screen.
        
        Args:
            screen: Pygame surface to draw on
        """
        # Draw background
        screen.fill((0, 0, 0))
        
        # Draw title
        title_text = self.font_large.render("Hand Drawing Game", True, (255, 255, 255))
        title_rect = title_text.get_rect(centerx=screen.get_width() // 2, y=100)
        screen.blit(title_text, title_rect)
        
        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        
        # Single Player button
        button_color = (100, 100, 255) if self.single_player_rect.collidepoint(mouse_pos) else (50, 50, 255)
        pygame.draw.rect(screen, button_color, self.single_player_rect, border_radius=10)
        text = self.font_normal.render("Single Player", True, (255, 255, 255))
        text_rect = text.get_rect(center=self.single_player_rect.center)
        screen.blit(text, text_rect)
        
        # Competitive button
        button_color = (100, 100, 255) if self.competitive_rect.collidepoint(mouse_pos) else (50, 50, 255)
        pygame.draw.rect(screen, button_color, self.competitive_rect, border_radius=10)
        text = self.font_normal.render("Competitive", True, (255, 255, 255))
        text_rect = text.get_rect(center=self.competitive_rect.center)
        screen.blit(text, text_rect)