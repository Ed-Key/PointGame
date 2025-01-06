from typing import Dict, Tuple
import pygame
from ..base import GameMode, GameConfig, GameStateType
from ..states.menu_state import MenuState
from ..states.playing_state import PlayingState
from ..states.results_state import ResultsState

class SinglePlayerMode(GameMode):
    """Implementation of single player game mode."""
    
    def __init__(self, screen_size: Tuple[int, int], config: GameConfig = None):
        """Initialize single player mode.
        
        Args:
            screen_size: Window size in pixels
            config: Optional game configuration
        """
        print("Initializing SinglePlayerMode...")  # Debug print
        if config is None:
            config = GameConfig()
        super().__init__(config)
        self.screen_size = screen_size
        
    def initialize(self) -> None:
        """Initialize single player mode states."""
        print("Setting up SinglePlayerMode states...")  # Debug print
        # Create all game states
        self.states = {
            GameStateType.PLAYING: PlayingState(self.screen_size),
            GameStateType.RESULTS: ResultsState(self.screen_size)
        }
        
        # Start with playing state
        self.current_state = self.states[GameStateType.PLAYING]
        print("SinglePlayerMode initialization complete")  # Debug print
    
    def start_new_game(self) -> None:
        """Start a new single player game."""
        print("Starting new single player game...")  # Debug print
        self.score = 0
        self.is_active = True
        if self.current_state:
            print("Calling on_enter for current state")  # Debug print
            self.current_state.on_enter()
        self.transition_to(GameStateType.PLAYING)
        print("New game started successfully")  # Debug print
        
    def end_game(self) -> None:
        """End the current game and show results."""
        results_state = self.states[GameStateType.RESULTS]
        results_state.set_results(
            score=self.score,
            accuracy=85.0,  # This should be calculated based on actual performance
            time_bonus=100,
            new_achievements=['First Game Completed']  # This should be dynamic
        )
        self.transition_to(GameStateType.RESULTS)
    
    def update(self, delta_time: float) -> None:
        """Update the game state.
        
        Args:
            delta_time: Time elapsed since last update
        """
        super().update(delta_time)
        
        # Add any single-player specific update logic here
        if self.current_state and self.current_state.next_state == GameStateType.PLAYING:
            # Update score based on current performance
            self.score = getattr(self.current_state, 'current_score', 0)