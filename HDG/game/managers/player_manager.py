# game/managers/player_manager.py
import pygame
from typing import Dict, Tuple
from ui.utils.colors import Colors  # Updated import path

class PlayerUIElement:
    """Individual player UI component."""
    
    def __init__(self, position: Tuple[int, int], name: str):
        self.position = position
        self.name = name
        self.font = pygame.font.Font(None, 36)
        self.width = 200
        self.height = 30
        
    def draw(self, screen: pygame.Surface, is_current: bool) -> None:
        """Draw the player UI element.
        
        Args:
            screen: Surface to draw on
            is_current: Whether this is the current player
        """
        # Create background
        background_color = Colors.BUTTON_HOVER if is_current else Colors.BUTTON_NORMAL
        rect = pygame.Rect(self.position[0], self.position[1], self.width, self.height)
        pygame.draw.rect(screen, background_color, rect)
        pygame.draw.rect(screen, Colors.BORDER, rect, 2)
        
        # Draw player name
        text = self.font.render(self.name, True, Colors.TEXT)
        text_rect = text.get_rect(
            center=(self.position[0] + self.width // 2,
                   self.position[1] + self.height // 2)
        )
        screen.blit(text, text_rect)

class PlayerDisplayManager:
    """Manages scalable player UI elements."""
    
    def __init__(self, base_position: Tuple[int, int], 
                 player_height: int, screen_width: int):
        self.base_position = base_position
        self.player_height = player_height
        self.screen_width = screen_width
        self.players: Dict[str, PlayerUIElement] = {}
    
    def add_player(self, player_id: str, name: str) -> None:
        """Add a new player UI element.
        
        Args:
            player_id: Player's unique ID
            name: Player's display name
        """
        position = (
            self.base_position[0],
            self.base_position[1] + len(self.players) * self.player_height
        )
        self.players[player_id] = PlayerUIElement(position, name)
    
    def draw(self, screen: pygame.Surface, current_player_id: str) -> None:
        """Draw all player UI elements.
        
        Args:
            screen: Surface to draw on
            current_player_id: ID of the current player
        """
        for player_id, ui_element in self.players.items():
            ui_element.draw(screen, is_current=player_id == current_player_id)