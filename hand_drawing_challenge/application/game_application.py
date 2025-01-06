# hand_drawing_challenge/application/game_application.py

import time
import pygame
from typing import Optional
from ..events.bus import EventBus
from ..events.types import GameEventType
from ..engine.game_engine import GameEngine
from ..input.manager import InputManager
from ..ui.manager import UIManager
from ..engine.modes.menu_mode import MenuMode
from .config import GameConfig

class GameApplication:
    """Main application class that coordinates game components."""

    def __init__(self, config: Optional[GameConfig] = None):
        """Initialize the game application."""
        self.config = config or GameConfig()
        self.event_bus = EventBus()

        # Initialize major subsystems
        self.engine = GameEngine(self.event_bus)
        self.ui_manager = UIManager(self.event_bus, self.config.screen_size)
        self.input_manager = InputManager(self.event_bus, self.config.camera_device)

        # Application state
        self.is_running = False
        self.last_update = None
        self.clock = pygame.time.Clock()

        # Register for events
        self.event_bus.subscribe(GameEventType.GAME_ENDED, self._handle_game_end)
        self.event_bus.subscribe(GameEventType.GAME_MODE_SELECTED, self._handle_mode_selected)

    def start(self, test_mode: bool = False) -> None:
        """Start the game application."""
        if self.is_running:
            return

        try:
            self.is_running = True
            self.last_update = time.time()

            # Initialize engine (this will start in menu mode)
            self.engine.initialize()

            # Start input processing if needed
            if not isinstance(self.engine.current_mode, MenuMode):
                self.input_manager.start()

            # Main game loop
            if not test_mode:
                while self.is_running:
                    self._process_frame()
                    self.clock.tick(self.config.fps)

        except Exception as e:
            print(f"Error in game loop: {e}")
            self.stop()

    def _process_frame(self) -> None:
        """Process a single frame."""
        # Process all pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop()
                return
            # Let current mode handle the event
            if self.engine.current_mode:
                self.engine.current_mode.handle_input(event)

        # Calculate delta time
        current_time = time.time()
        delta_time = current_time - self.last_update
        self.last_update = current_time

        # Update engine and current mode
        self.engine.update(delta_time)

        # Only process input and update UI for non-menu modes
        if not isinstance(self.engine.current_mode, MenuMode):
            self.input_manager.process_input()
            frame = self.input_manager.get_frame()
            if frame is not None:
                self.ui_manager.update_frame(frame)
            self.ui_manager.update(delta_time)
            self.ui_manager.render()

        # Update display
        pygame.display.flip()

    def _handle_mode_selected(self, event_type: GameEventType, data: dict) -> None:
        """Handle game mode selection."""
        mode = data.get("mode")
        if mode:
            # Start input processing when transitioning from menu to game mode
            self.input_manager.start()

    def stop(self) -> None:
        """Stop the game application."""
        if not self.is_running:
            return

        try:
            self.is_running = False
            self.event_bus.publish(GameEventType.GAME_ENDED)
            self.input_manager.stop()
            self.cleanup()
        except Exception as e:
            print(f"Error during shutdown: {e}")

    def cleanup(self) -> None:
        """Clean up resources."""
        self.event_bus.clear_subscribers()
        self.input_manager.cleanup()

    def _handle_game_end(self, event_type: GameEventType, data: Optional[dict] = None) -> None:
        """Handle game end event."""
        self.is_running = False
