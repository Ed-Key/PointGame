import time
import logging
import pygame
from typing import Optional
from .config import GameConfig
from ..events.bus import EventBus
from ..events.types import GameEventType
from ..engine.game_engine import GameEngine
from ..ui.manager import UIManager
from ..engine.modes.menu_mode import MenuMode

class GameApplication:
    """Main application class that coordinates game components."""
    
    def __init__(self, config: Optional[GameConfig] = None):
        """Initialize the game application."""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        try:
            self.logger.info("Initializing game application")
            
            # Initialize core systems
            self.config = config or GameConfig()
            self.event_bus = EventBus()
            
            # Initialize pygame
            pygame.init()
            pygame.font.init()
            
            # Initialize UI manager first (will create input manager)
            self.ui_manager = UIManager(self.event_bus, self.config.screen_size)
            
            # Initialize engine with UI manager
            self.engine = GameEngine(self.event_bus, self.ui_manager)

            self.ui_manager.start_input_processing()

            # Application state
            self.is_running = False
            self.last_update = None
            self.clock = pygame.time.Clock()
            self._cleanup_done = False
            
            # Register for events
            self.event_bus.subscribe(GameEventType.GAME_ENDED, self._handle_game_end)
            self.event_bus.subscribe(GameEventType.GAME_MODE_SELECTED, self._handle_mode_selected)
            
        except Exception as e:
            self.logger.critical(f"Failed to initialize game application: {e}")
            self.cleanup()
            raise
    
    def start(self, test_mode: bool = False) -> None:
        """Start the game application."""
        if self.is_running:
            return
            
        try:
            self.logger.info("Starting game application")
            self.is_running = True
            self.last_update = time.time()
            
            # Initialize engine
            self.engine.initialize()
            
            # Main game loop
            if not test_mode:
                while self.is_running:
                    self._process_frame()
                    self.clock.tick(self.config.fps)
                    
        except Exception as e:
            self.logger.error(f"Error in game loop: {e}")
            self.stop()
            
        finally:
            self.cleanup()
    
    def _process_frame(self) -> None:
        """Process a single frame of the game loop."""
        try:
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
            
            # Update engine and UI components
            self.engine.update(delta_time)
            
            # Update UI and display
            if not isinstance(self.engine.current_mode, MenuMode):
                self.ui_manager.update(delta_time)
                self.ui_manager.render()
            
            # Update display
            pygame.display.flip()
            
        except Exception as e:
            self.logger.error(f"Error processing frame: {e}")
            # Continue running unless critical error
    
    def _handle_mode_selected(self, event_type: GameEventType, data: Optional[dict] = None) -> None:
        """Handle game mode selection event."""
        try:
            mode = data.get("mode")
            if mode:
                # Stop input processing if we're returning to menu
                if mode == "menu":
                    self.logger.info("Returning to menu, stopping input processing")
                    self.ui_manager.stop_input_processing()
                # Don't start input processing here - let the game mode handle it
        except Exception as e:
            self.logger.error(f"Error handling mode selection: {e}")
    
    def stop(self) -> None:
        """Stop the game application."""
        if not self.is_running:
            return
            
        try:
            self.logger.info("Stopping game application")
            self.is_running = False
            
            # First stop input processing
            if hasattr(self, 'ui_manager'):
                self.ui_manager.stop_input_processing()
            
            # Then publish game ended event
            if hasattr(self, 'event_bus'):
                self.event_bus.publish(GameEventType.GAME_ENDED)
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            
        finally:
            self.cleanup()
    
    def cleanup(self) -> None:
        """Clean up application resources."""
        # Guard against multiple cleanups
        if getattr(self, '_cleanup_done', False):
            return
            
        try:
            self.logger.info("Cleaning up resources")
            
            # First unsubscribe from our own events
            if hasattr(self, 'event_bus'):
                self.event_bus.unsubscribe(GameEventType.GAME_ENDED, self._handle_game_end)
                self.event_bus.unsubscribe(GameEventType.GAME_MODE_SELECTED, self._handle_mode_selected)
            
            # Then cleanup engine (which will unsubscribe its events)
            if hasattr(self, 'engine'):
                self.engine.cleanup()
            
            # Then cleanup UI manager (which handles input cleanup)
            if hasattr(self, 'ui_manager'):
                self.ui_manager.cleanup()
            
            # Finally clear all remaining subscribers and null event bus
            if hasattr(self, 'event_bus'):
                self.event_bus.clear_subscribers()
                self.event_bus = None
            
            # Quit pygame last
            pygame.quit()
            
            self._cleanup_done = True
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def _handle_game_end(self, event_type: GameEventType, data: Optional[dict] = None) -> None:
        """Handle game end event."""
        self.logger.info("Handling game end event")
        self.is_running = False
    
    def get_fps(self) -> float:
        """Get current frames per second."""
        return self.clock.get_fps()
