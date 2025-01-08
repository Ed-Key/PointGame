# hand_drawing_challenge/engine/game_engine.py

import logging
from typing import Optional, Dict, Any
from ..events.bus import EventBus
from ..events.types import GameEventType
from .state_machine import GameStateMachine, GameState
from .modes.menu_mode import MenuMode
from .modes.single_player import SinglePlayerMode
from .modes.competitive import CompetitiveMode
from .modes.base_mode import GameMode
from ..ui.manager import UIManager

class GameEngine:
    """Core game engine that coordinates states and modes.
    
    The GameEngine is responsible for:
    - Managing game states through a state machine
    - Handling transitions between game modes
    - Coordinating event communication
    - Updating game logic
    
    Attributes:
        event_bus (EventBus): Central event bus for communication
        ui_manager (UIManager): Manager for UI components
        state_machine (GameStateMachine): Manages game states
        current_mode (Optional[GameMode]): Currently active game mode
        is_running (bool): Whether the engine is currently running
    """
    
    def __init__(self, event_bus: EventBus, ui_manager: UIManager):
        """Initialize the game engine.
        
        Args:
            event_bus: Central event bus for communication
            ui_manager: Manager for UI components
        """
        self.event_bus = event_bus
        self.ui_manager = ui_manager
        self.state_machine = GameStateMachine()
        self.current_mode: Optional[GameMode] = None
        self.is_running = False
        
        # Initialize logging
        self.logger = logging.getLogger(__name__)
        
        # Register for events
        self.event_bus.subscribe(GameEventType.GAME_ENDED, self._handle_game_end)
        self.event_bus.subscribe(GameEventType.GAME_MODE_SELECTED, self._handle_mode_selected)
        self.event_bus.subscribe(GameEventType.MENU_BACK, self._handle_menu_return)

    
    def initialize(self) -> None:
        """Initialize the game engine and states.
        
        Sets up initial game state and starts in menu mode.
        """
        try:
            self.logger.info("Initializing game engine")
            self.is_running = True
            
            # Start with menu mode
            self.change_mode(MenuMode(self.event_bus))
            
        except Exception as e:
            self.logger.error(f"Failed to initialize game engine: {e}")
            self.is_running = False
            raise
    
    def update(self, delta_time: float) -> None:
        """Update game state.
        
        Args:
            delta_time: Time elapsed since last update in seconds
        """
        if not self.is_running:
            return
            
        try:
            # Update current game mode if active
            if self.current_mode and self.current_mode.is_active:
                self.current_mode.update(delta_time)
                
        except Exception as e:
            self.logger.error(f"Error during game update: {e}")
            # Don't stop the engine, but log the error
    
    def change_mode(self, mode: GameMode) -> None:
        """Change to a new game mode."""
        try:
            self.logger.info(f"Changing game mode to: {mode.__class__.__name__}")
            
            # Store current mode
            old_mode = self.current_mode
            # Clear current mode before stopping to prevent recursion
            self.current_mode = None
            
            # Stop old mode if it exists
            if old_mode:
                try:
                    old_mode.stop()
                except Exception as e:
                    self.logger.error(f"Error stopping old mode: {e}")
                    
            # Initialize and start new mode
            try:
                self.current_mode = mode
                self.current_mode.initialize()
                self.current_mode.start()
            except Exception as e:
                self.logger.error(f"Error starting new mode: {e}")
                self._recover_to_menu()
                
        except Exception as e:
            self.logger.error(f"Failed to change game mode: {e}")
            self._recover_to_menu()
    
    def _handle_game_end(self, event_type: GameEventType, data: Optional[dict] = None) -> None:
        """Handle game end event.
        
        Stops the engine and current mode.
        
        Args:
            event_type: Type of event (GAME_ENDED)
            data: Optional event data
        """
        self.logger.info("Handling game end event")
        self.is_running = False
        if self.current_mode:
            self.current_mode.stop()
    
    def _handle_mode_selected(self, event_type: GameEventType, data: dict) -> None:
        """Handle game mode selection.
        
        Creates and switches to the selected game mode.
        
        Args:
            event_type: Type of event (GAME_MODE_SELECTED)
            data: Contains the selected mode
        """
        try:
            mode = data.get("mode")
            self.logger.info(f"Mode selection received: {mode}")
            
            if mode == "single_player":
                self.change_mode(SinglePlayerMode(self.event_bus, self.ui_manager))
            elif mode == "competitive":
                self.change_mode(CompetitiveMode(self.event_bus))
            else:
                self.logger.warning(f"Unknown game mode selected: {mode}")
                
        except Exception as e:
            self.logger.error(f"Error handling mode selection: {e}")
            self._recover_to_menu()
    
    def _recover_to_menu(self) -> None:
        """Recovery method to return to menu mode in case of errors."""
        try:
            self.logger.info("Attempting recovery to menu mode")
            self.change_mode(MenuMode(self.event_bus))
        except Exception as e:
            self.logger.critical(f"Failed to recover to menu mode: {e}")
            self.is_running = False
    
    def cleanup(self) -> None:
        """Clean up engine resources.
        
        Should be called before shutting down the game.
        """
        try:
            self.logger.info("Cleaning up game engine resources")
            if self.current_mode:
                self.current_mode.stop()
            self.event_bus.clear_subscribers()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            
    def get_current_state(self) -> Optional[GameState]:
        """Get the current game state.
        
        Returns:
            Optional[GameState]: Current state or None if not available
        """
        return self.state_machine.current_state if self.state_machine else None
    
    def _handle_menu_return(self, event_type: GameEventType, data: Any) -> None:
        """Handle return to menu event.
        
        Args:
            event_type: Type of event
            data: Event data
        """
        try:
            self.logger.info("Returning to menu")
            old_mode = self.current_mode
            self.current_mode = None

            if old_mode:
                try:
                    old_mode.stop()
                except Exception as e:
                    self.logger.error(f"Error stopping old mode: {e}")

            self.change_mode(MenuMode(self.event_bus))
        except Exception as e:
            self.logger.error(f"Error returning to menu: {e}")
            self._recover_to_menu()