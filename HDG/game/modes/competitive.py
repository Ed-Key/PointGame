# game/modes/competitive.py
from typing import Dict, Tuple, Optional, Any
import pygame
import numpy as np
from ..base import GameMode, GameConfig, GameStateType
from ..states.playing_state import PlayingState
from ..states.results_state import ResultsState
from ..managers import CompetitiveGameManager, PlayerDisplayManager
from ui.utils.colors import Colors

class CompetitivePlayingState(PlayingState):
    """Extended playing state for turn-based competitive mode."""
    
    def __init__(self, screen_size: Tuple[int, int]):
        """Initialize competitive playing state."""
        super().__init__(screen_size)
        self.game_manager = CompetitiveGameManager()
        self.setup_competitive_ui()
        
        # Initialize with some test players
        self.add_player("Player 1")
        self.add_player("Player 2")
        self.add_player("Player 3")  # Now supports 3+ players!
    
    def setup_competitive_ui(self) -> None:
        """Setup UI elements specific to competitive mode."""
        self.player_font = pygame.font.Font(None, 48)
        self.player_display = PlayerDisplayManager(
            base_position=(20, 20),
            player_height=40,
            screen_width=self.screen_size[0]
        )
    
    def add_player(self, name: str) -> None:
        """Add a new player to the game."""
        player_id = self.game_manager.add_player(name)
        self.player_display.add_player(player_id, name)
    
    def update(self, delta_time: float) -> None:
        """Update competitive playing state."""
        if self.is_paused:
            return
            
        # Update time
        self.time_remaining -= delta_time
        if self.time_remaining <= 0:
            self.next_player()
            return
            
        # Update score display
        self.score_display.update(
            score=self.current_score,
            game_state="Playing",
            is_drawing=self.is_drawing
        )
    
    def draw(self) -> None:
        """Draw the competitive state."""
        # Draw base state (canvas, pattern, etc.)
        super().draw()
        
        screen = pygame.display.get_surface()
        
        # Draw player informati on
        self.player_display.draw(screen, self.game_manager.get_current_player())
        
        if self.is_paused:
            self._draw_pause_overlay(screen)
    
    def next_player(self) -> None:
        """Switch to the next player's turn."""
        # Save current player's score
        current_player = self.game_manager.get_current_player()
        if current_player:
            self.game_manager.update_player_score(current_player, self.current_score)
        
        # Move to next player
        next_player = self.game_manager.next_turn()
        if next_player is None:
            self.transition_to(GameStateType.RESULTS)
            return
            
        # Reset state for next player
        self.time_remaining = 60.0
        self.current_score = 0
        self.is_drawing = False
        self.canvas = np.zeros((480, 640, 3), dtype=np.uint8)
        self.drawing_tracker.clear()

    def handle_input(self, event: Any) -> None:
        """Handle input events."""
        super().handle_input(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:  # Enter key ends turn early
                self.next_player()

class CompetitiveMode(GameMode):
    """Implementation of turn-based competitive mode."""
    
    def __init__(self, screen_size: Tuple[int, int], config: GameConfig = None):
        """Initialize competitive mode."""
        if config is None:
            config = GameConfig()
        super().__init__(config)
        self.screen_size = screen_size
    
    def initialize(self) -> None:
        """Initialize competitive mode states."""
        self.states = {
            GameStateType.PLAYING: CompetitivePlayingState(self.screen_size),
            GameStateType.RESULTS: ResultsState(self.screen_size)
        }
        
        # Start with playing state since we're already in a game mode
        self.current_state = self.states[GameStateType.PLAYING]