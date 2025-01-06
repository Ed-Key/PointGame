# hand_drawing_challenge/engine/game_engine.py

import pygame
from typing import Optional, Dict
from ..events.bus import EventBus
from ..events.types import GameEventType
from .state_machine import GameStateMachine, GameState
from .modes.menu_mode import MenuMode
from .modes.single_player import SinglePlayerMode
from .modes.competitive import CompetitiveMode
from .modes.base_mode import GameMode

class GameEngine:
    """Core game engine that coordinates states and modes."""
    
    def __init__(self, event_bus: EventBus):
        """Initialize the game engine.
        
        Args:
            event_bus: Central event bus for communication
        """
        self.event_bus = event_bus
        self.state_machine = GameStateMachine()
        self.current_mode: Optional[GameMode] = None
        self.is_running = False
        
        # Register for events
        self.event_bus.subscribe(GameEventType.GAME_ENDED, self._handle_game_end)
        self.event_bus.subscribe(GameEventType.GAME_MODE_SELECTED, self._handle_mode_selected)
    
    def initialize(self) -> None:
        """Initialize the game engine and states."""
        self.is_running = True
        
        # Start with menu mode
        self.change_mode(MenuMode(self.event_bus))
    
    def update(self, delta_time: float) -> None:
        """Update game state.
        
        Args:
            delta_time: Time elapsed since last update
        """
        if not self.is_running:
            return
            
        # Update current game mode if active
        if self.current_mode and self.current_mode.is_active:
            self.current_mode.update(delta_time)
    
    def change_mode(self, mode: GameMode) -> None:
        """Change to a new game mode.
        
        Args:
            mode: New game mode to switch to
        """
        if self.current_mode:
            self.current_mode.stop()
            
        self.current_mode = mode
        self.current_mode.initialize()
        self.current_mode.start()
    
    def _handle_game_end(self, event_type: GameEventType, data: Optional[dict] = None) -> None:
        """Handle game end event."""
        self.is_running = False
        if self.current_mode:
            self.current_mode.stop()
    
    def _handle_mode_selected(self, event_type: GameEventType, data: dict) -> None:
        """Handle game mode selection."""
        mode = data.get("mode")
        if mode == "single_player":
            self.change_mode(SinglePlayerMode(self.event_bus))
        elif mode == "competitive":
            self.change_mode(CompetitiveMode(self.event_bus))