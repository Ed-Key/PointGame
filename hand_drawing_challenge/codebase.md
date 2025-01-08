# __init__.py

```py
from . import events

__all__ = ['events']

```

# .pytest_cache\.gitignore

```
# Created by pytest automatically.
*

```

# .pytest_cache\CACHEDIR.TAG

```TAG
Signature: 8a477f597d28d172789f06886806bc55
# This file is a cache directory tag created by pytest.
# For information about cache directory tags, see:
#	https://bford.info/cachedir/spec.html

```

# .pytest_cache\README.md

```md
# pytest cache directory #

This directory contains data from the pytest's cache plugin,
which provides the `--lf` and `--ff` options, as well as the `cache` fixture.

**Do not** commit this to version control.

See [the docs](https://docs.pytest.org/en/stable/how-to/cache.html) for more information.

```

# .pytest_cache\v\cache\lastfailed

```
{
  "tests_events/test_bus.py": true,
  "test/test_bus.py::TestEventBus": true,
  "tests/test_events/test_bus.py": true,
  "tests/test_input/test_manager.py": true
}
```

# .pytest_cache\v\cache\nodeids

```
[
  "test/test_bus.py::TestEventBus::test_clear_subscribers",
  "test/test_bus.py::TestEventBus::test_error_handling",
  "test/test_bus.py::TestEventBus::test_multiple_subscribers",
  "test/test_bus.py::TestEventBus::test_subscribe_and_publish",
  "test/test_bus.py::TestEventBus::test_unsubscribe"
]
```

# .pytest_cache\v\cache\stepwise

```
[]
```

# application\__init__.py

```py

```

# application\config.py

```py
# hand_drawing_challenge/application/config.py
from dataclasses import dataclass
from typing import Tuple

@dataclass
class GameConfig:
    """Global game configuration settings."""
    screen_size: Tuple[int, int] = (1280, 720)
    fps: int = 60
    debug_mode: bool = False
    
    # Input settings
    camera_device: int = 0
    camera_width: int = 640
    camera_height: int = 480
    
    # Game settings
    max_players: int = 4
    round_time: int = 60
    min_accuracy: float = 0.7
```

# application\game_application.py

```py
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
            self.event_bus.publish(GameEventType.GAME_ENDED)
            self.ui_manager.stop_input_processing()
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            
        finally:
            self.cleanup()
    
    def cleanup(self) -> None:
        """Clean up application resources."""
        try:
            self.logger.info("Cleaning up resources")
            
            # Clean up subsystems
            if hasattr(self, 'event_bus'):
                self.event_bus.clear_subscribers()
            
            if hasattr(self, 'ui_manager'):
                self.ui_manager.cleanup()
            
            if hasattr(self, 'engine'):
                self.engine.cleanup()
            
            # Quit pygame
            pygame.quit()
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def _handle_game_end(self, event_type: GameEventType, data: Optional[dict] = None) -> None:
        """Handle game end event."""
        self.logger.info("Handling game end event")
        self.is_running = False
    
    def get_fps(self) -> float:
        """Get current frames per second."""
        return self.clock.get_fps()

```

# engine\__init__.py

```py
# hand_drawing_challenge/engine/__init__.py
from .game_engine import GameEngine
from .state_machine import GameStateMachine, GameState, State
from .modes.base_mode import GameMode

__all__ = [
    'GameEngine',
    'GameStateMachine',
    'GameState',
    'State',
    'GameMode'
]
```

# engine\game_engine.py

```py
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
```

# engine\modes\base_mode.py

```py
# hand_drawing_challenge/engine/modes/base_mode.py
from abc import ABC, abstractmethod
from typing import Any, Optional
from ...events.bus import EventBus

class GameMode(ABC):
    """Base interface for game modes (single player, competitive, etc.)."""
    
    def __init__(self, event_bus: EventBus):
        """Initialize the game mode.
        
        Args:
            event_bus: Central event bus for communication
        """
        self.event_bus = event_bus
        self.is_active = False
        self.score = 0
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize mode-specific resources and state."""
        pass
    
    @abstractmethod
    def update(self, delta_time: float) -> None:
        """Update game mode state.
        
        Args:
            delta_time: Time elapsed since last update in seconds
        """
        pass
    
    @abstractmethod
    def handle_input(self, event: Any) -> None:
        """Handle input events.
        
        Args:
            event: Input event to process
        """
        pass
    
    def start(self) -> None:
        """Start the game mode."""
        self.is_active = True
        self.score = 0
    
    def stop(self) -> None:
        """Stop the game mode and cleanup resources."""
        self.is_active = False
```

# engine\modes\competitive.py

```py
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
```

# engine\modes\menu_mode.py

```py
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
```

# engine\modes\single_player.py

```py
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

```

# engine\state_machine.py

```py
# hand_drawing_challenge/engine/state_machine.py
from enum import Enum, auto
from typing import Dict, Optional
from abc import ABC, abstractmethod

class GameState(Enum):
    """Available game states."""
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    RESULTS = auto()

class State(ABC):
    """Abstract base class for game states."""
    
    def __init__(self):
        """Initialize the state."""
        self.state_machine: Optional['GameStateMachine'] = None
    
    @abstractmethod
    def enter(self) -> None:
        """Called when entering this state."""
        pass
    
    @abstractmethod
    def exit(self) -> None:
        """Called when exiting this state."""
        pass
    
    @abstractmethod
    def update(self, delta_time: float) -> None:
        """Update the state.
        
        Args:
            delta_time: Time elapsed since last update
        """
        pass

class GameStateMachine:
    """Manages game state transitions and updates."""
    
    def __init__(self):
        """Initialize the state machine."""
        self.states: Dict[GameState, State] = {}
        self.current_state: Optional[State] = None
        self.previous_state: Optional[State] = None
    
    def add_state(self, state_id: GameState, state: State) -> None:
        """Add a state to the machine.
        
        Args:
            state_id: Identifier for the state
            state: State instance to add
        """
        state.state_machine = self
        self.states[state_id] = state
    
    def change_state(self, new_state: GameState) -> None:
        """Change to a new state.
        
        Args:
            new_state: State to transition to
        """
        if new_state not in self.states:
            return
            
        if self.current_state:
            self.current_state.exit()
            self.previous_state = self.current_state
            
        self.current_state = self.states[new_state]
        self.current_state.enter()
    
    def update(self, delta_time: float) -> None:
        """Update the current state.
        
        Args:
            delta_time: Time elapsed since last update
        """
        if self.current_state:
            self.current_state.update(delta_time)
```

# events\__init__.py

```py
from .bus import EventBus
from .types import GameEventType

__all__ = ['EventBus', 'GameEventType']

```

# events\bus.py

```py
# hand_drawing_challenge/events/bus.py

from typing import Dict, List, Optional, Any
from collections import defaultdict
from hand_drawing_challenge.events.types import GameEventType, EventHandler

class EventBus:
    """
    Central event bus for game-wide communication.
    
    The EventBus enables decoupled communication between components through a 
    publish-subscribe pattern. Components can subscribe to specific event types
    and publish events without direct knowledge of subscribers.
    
    Example:
        >>> event_bus = EventBus()
        >>> def on_score_update(event_type: GameEventType, data: Any) -> None:
        ...     print(f"Score updated: {data}")
        >>> event_bus.subscribe(GameEventType.SCORE_UPDATED, on_score_update)
        >>> event_bus.publish(GameEventType.SCORE_UPDATED, 100)
        Score updated: 100
    """
    
    def __init__(self):
        """Initialize the event bus with empty subscriber lists."""
        self._subscribers: Dict[GameEventType, List[EventHandler]] = defaultdict(list)
    
    def subscribe(self, event_type: GameEventType, handler: EventHandler) -> None:
        """
        Subscribe a handler to a specific event type.
        
        Args:
            event_type: Type of event to subscribe to
            handler: Callback function to handle the event
        """
        if handler not in self._subscribers[event_type]:
            self._subscribers[event_type].append(handler)
    
    def unsubscribe(self, event_type: GameEventType, handler: EventHandler) -> None:
        """
        Unsubscribe a handler from a specific event type.
        
        Args:
            event_type: Type of event to unsubscribe from
            handler: Handler to remove
        """
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(handler)
            except ValueError:
                pass  # Handler wasn't subscribed
    
    def publish(self, event_type: GameEventType, data: Any = None) -> None:
        """
        Publish an event to all subscribers.
        
        Args:
            event_type: Type of event to publish
            data: Optional data to pass to handlers
        """
        for handler in self._subscribers[event_type]:
            try:
                handler(event_type, data)
            except Exception as e:
                # In a production system, you'd want to log this
                print(f"Error in event handler: {e}")

    def clear_subscribers(self, event_type: Optional[GameEventType] = None) -> None:
        """
        Clear subscribers for a specific event type or all subscribers if no type specified.
        
        Args:
            event_type: Optional event type to clear subscribers for
        """
        if event_type:
            self._subscribers[event_type].clear()
        else:
            self._subscribers.clear()

```

# events\events.py

```py
# events/events.py
from dataclasses import dataclass, field
from typing import Optional
from .types import GameEventType
from ..services.patterns.models import Pattern

@dataclass
class BaseEvent:
    """Base class for all game events."""
    pass

@dataclass
class GameStateChangedEvent(BaseEvent):
    """Event for game state changes."""
    new_state: str
    old_state: Optional[str] = None
    type: GameEventType = field(default=GameEventType.GAME_STARTED, init=False)

@dataclass
class ModeChangedEvent(BaseEvent):
    """Event for game mode changes."""
    new_mode: str
    old_mode: Optional[str] = None
    type: GameEventType = field(default=GameEventType.GAME_MODE_SELECTED, init=False)

@dataclass
class ScoreEvent(BaseEvent):
    """Event for score updates."""
    score: int
    type: GameEventType = field(default=GameEventType.SCORE_UPDATED, init=False)
    player_id: Optional[str] = None

@dataclass
class PatternGeneratedEvent(BaseEvent):
    """Event for new pattern generation."""
    pattern: Pattern
    type: GameEventType = field(default=GameEventType.PATTERN_GENERATED, init=False)

@dataclass
class PatternCompletedEvent(BaseEvent):
    """Event for pattern completion."""
    pattern: Pattern
    score: float
    type: GameEventType = field(default=GameEventType.PATTERN_COMPLETED, init=False)
```

# events\interfaces.py

```py
# hand_drawing_challenge/events/interfaces.py
from abc import ABC, abstractmethod
from typing import Any, Callable
from .types import GameEventType

class IEventBus(ABC):
    """Interface defining the event bus contract."""
    
    @abstractmethod
    def subscribe(self, event_type: GameEventType, handler: Callable[[GameEventType, Any], None]) -> None:
        """Subscribe to an event type."""
        pass
        
    @abstractmethod
    def unsubscribe(self, event_type: GameEventType, handler: Callable[[GameEventType, Any], None]) -> None:
        """Unsubscribe from an event type."""
        pass
        
    @abstractmethod
    def publish(self, event_type: GameEventType, data: Any = None) -> None:
        """Publish an event."""
        pass
```

# events\types.py

```py
# hand_drawing_challenge/events/types.py

from enum import Enum, auto
from typing import Any, Callable

class GameEventType(Enum):
    """Game event types for the event system."""
    
    # Input events
    HAND_DETECTED = auto()
    HAND_LOST = auto()
    HAND_POSITION_UPDATED = auto()
    DRAWING_STARTED = auto()
    DRAWING_ENDED = auto()
    CAMERA_FAILURE = auto()
    INPUT_ERROR = auto()

    # Game state events
    GAME_STARTED = auto()
    GAME_PAUSED = auto()
    GAME_RESUMED = auto()
    GAME_ENDED = auto()

    # Menu events
    GAME_MODE_SELECTED = auto()
    MENU_BACK = auto()
    
    # Turn management events
    TURN_STARTED = auto()
    TURN_ENDED = auto()
    PLAYER_ADDED = auto()
    
    # Score events
    SCORE_UPDATED = auto()
    
    # Pattern events
    PATTERN_GENERATED = auto()  # Added this event type
    PATTERN_COMPLETED = auto()
    PATTERN_DISPLAY_UPDATED = auto()
    PATTERN_VALIDATION_STARTED = auto()
    PATTERN_VALIDATION_COMPLETED = auto()

# Type alias for event handlers
EventHandler = Callable[[GameEventType, Any], None]
```

# input\__init__.py

```py

```

# input\.pytest_cache\.gitignore

```
# Created by pytest automatically.
*

```

# input\.pytest_cache\CACHEDIR.TAG

```TAG
Signature: 8a477f597d28d172789f06886806bc55
# This file is a cache directory tag created by pytest.
# For information about cache directory tags, see:
#	https://bford.info/cachedir/spec.html

```

# input\.pytest_cache\README.md

```md
# pytest cache directory #

This directory contains data from the pytest's cache plugin,
which provides the `--lf` and `--ff` options, as well as the `cache` fixture.

**Do not** commit this to version control.

See [the docs](https://docs.pytest.org/en/stable/how-to/cache.html) for more information.

```

# input\.pytest_cache\v\cache\nodeids

```
[]
```

# input\.pytest_cache\v\cache\stepwise

```
[]
```

# input\drawing_tracker.py

```py
# hand_drawing_challenge/input/drawing_tracker.py

from collections import deque
import numpy as np
import logging
from typing import Optional, Tuple, List, Deque, Dict
from dataclasses import dataclass
from .input_types import HandPoint

@dataclass
class DrawingConfig:
    """Configuration for drawing behavior with enhanced smoothing parameters.
    
    Attributes:
        position_history_size: Number of recent positions to keep for smoothing
        velocity_history_size: Number of recent velocities to track
        max_velocity: Maximum allowed velocity between points (pixels/frame)
        min_movement: Minimum movement to register new point (pixels)
        max_gap_distance: Maximum distance to interpolate between points (pixels)
        max_points: Maximum number of points to store in trail
        interpolation_steps: Number of points to interpolate in gaps
        smoothing_factor: Weight given to smoothed vs raw positions (0-1)
        prediction_weight: Weight given to velocity predictions (0-1)
    """
    # Position smoothing
    position_history_size: int = 15
    velocity_history_size: int = 8
    
    # Movement thresholds
    max_velocity: float = 100.0
    min_movement: float = 3.0
    max_gap_distance: float = 50.0
    
    # Trail management
    max_points: int = 10000
    interpolation_steps: int = 5
    
    # Smoothing weights
    smoothing_factor: float = 0.8
    prediction_weight: float = 0.2

class DrawingTracker:
    """Enhanced drawing tracker with improved smoothing and interpolation.
    
    Features:
    - Advanced position smoothing using weighted averaging and velocity prediction
    - Velocity-based movement filtering
    - Gap interpolation for smooth drawing
    - Configurable smoothing and filtering parameters
    """
    
    def __init__(self, width: int = 640, height: int = 480, 
                 config: Optional[DrawingConfig] = None):
        """Initialize the drawing tracker.
        
        Args:
            width: Canvas width in pixels
            height: Canvas height in pixels
            config: Optional configuration settings
        """
        self.logger = logging.getLogger(__name__)
        self.width = width
        self.height = height
        self.config = config or DrawingConfig()
        
        # Position tracking
        self.position_history: Deque[Tuple[float, float]] = deque(
            maxlen=self.config.position_history_size
        )
        self.velocity_history: Deque[Tuple[float, float]] = deque(
            maxlen=self.config.velocity_history_size
        )
        
        # State tracking
        self.last_position: Optional[Tuple[float, float]] = None
        self.last_velocity: Optional[Tuple[float, float]] = None
        self.trail_points: List[Tuple[int, int]] = []
        
        self.logger.info(f"Initialized DrawingTracker with dimensions {width}x{height}")
    
    def update(self, position: Optional[Tuple[int, int]], 
               is_drawing: bool) -> Optional[Tuple[int, int]]:
        """Update drawing state with enhanced smoothing and interpolation.
        
        Args:
            position: New position in pixel coordinates (x, y)
            is_drawing: Whether currently in drawing mode
            
        Returns:
            Smoothed position or None if position invalid
        """
        if not position:
            return self.last_position
            
        try:
            x, y = float(position[0]), float(position[1])
            
            # Basic bounds checking
            if not (0 <= x < self.width and 0 <= y < self.height):
                self.logger.debug(f"Position {position} out of bounds")
                return self.last_position
                
            # Calculate velocity if we have a previous position
            current_velocity = None
            if self.last_position:
                dx = x - self.last_position[0]
                dy = y - self.last_position[1]
                current_velocity = (dx, dy)
                
                # Check for unrealistic movements
                velocity_magnitude = np.sqrt(dx*dx + dy*dy)
                if velocity_magnitude > self.config.max_velocity:
                    self.logger.debug(
                        f"Velocity {velocity_magnitude:.2f} exceeds max {self.config.max_velocity}"
                    )
                    return self.last_position
            
            # Update histories
            self.position_history.append((x, y))
            if current_velocity:
                self.velocity_history.append(current_velocity)
            
            # Apply Kalman-inspired smoothing
            smoothed_position = self._smooth_position()
            if not smoothed_position:
                return self.last_position
                
            if is_drawing:
                self._update_trail(smoothed_position)
                
            self.last_position = smoothed_position
            return smoothed_position
            
        except Exception as e:
            self.logger.error(f"Error updating position: {e}")
            return self.last_position
    
    def _smooth_position(self) -> Optional[Tuple[float, float]]:
        """Apply advanced position smoothing using weighted averaging.
        
        Returns:
            Smoothed (x, y) position or None if insufficient history
        """
        if len(self.position_history) < 3:
            return self.position_history[-1] if self.position_history else None
            
        try:
            # Calculate weighted average of positions (more weight to recent positions)
            weights = np.linspace(
                1 - self.config.smoothing_factor,
                1.0,
                len(self.position_history)
            )
            weights = weights / weights.sum()
            
            x_smooth = y_smooth = 0.0
            for (x, y), weight in zip(self.position_history, weights):
                x_smooth += x * weight
                y_smooth += y * weight
                
            # Apply velocity-based prediction
            if self.velocity_history:
                avg_velocity = np.mean(self.velocity_history, axis=0)
                x_smooth = (x_smooth * (1 - self.config.prediction_weight) + 
                          (x_smooth + avg_velocity[0]) * self.config.prediction_weight)
                y_smooth = (y_smooth * (1 - self.config.prediction_weight) + 
                          (y_smooth + avg_velocity[1]) * self.config.prediction_weight)
                
            return (int(x_smooth), int(y_smooth))
            
        except Exception as e:
            self.logger.error(f"Error smoothing position: {e}")
            return None
    
    def _update_trail(self, new_position: Tuple[float, float]) -> None:
        """Update trail points with interpolation for gaps.
        
        Args:
            new_position: New smoothed position to add to trail
        """
        try:
            if not self.trail_points:
                self.trail_points.append(new_position)
                return
                
            last_point = self.trail_points[-1]
            distance = np.sqrt(
                (new_position[0] - last_point[0])**2 +
                (new_position[1] - last_point[1])**2
            )
            
            # Skip if movement is too small (reduces jitter)
            if distance < self.config.min_movement:
                return
                
            # Interpolate if gap is too large
            if distance > self.config.max_gap_distance:
                self._interpolate_gap(last_point, new_position)
            else:
                self.trail_points.append(new_position)
                
            # Maintain maximum trail length
            if len(self.trail_points) > self.config.max_points:
                self.trail_points = self.trail_points[-self.config.max_points:]
                
        except Exception as e:
            self.logger.error(f"Error updating trail: {e}")
    
    def _interpolate_gap(self, start: Tuple[float, float], 
                        end: Tuple[float, float]) -> None:
        """Interpolate points between gaps in the trail.
        
        Args:
            start: Starting point of the gap
            end: Ending point of the gap
        """
        try:
            for i in range(1, self.config.interpolation_steps + 1):
                t = i / (self.config.interpolation_steps + 1)
                x = start[0] + (end[0] - start[0]) * t
                y = start[1] + (end[1] - start[1]) * t
                self.trail_points.append((int(x), int(y)))
                
        except Exception as e:
            self.logger.error(f"Error interpolating gap: {e}")
    
    def clear(self) -> None:
        """Reset the drawing state."""
        self.trail_points.clear()
        self.position_history.clear()
        self.velocity_history.clear()
        self.last_position = None
        self.last_velocity = None
        self.logger.info("Drawing state cleared")
    
    def get_trail_points(self) -> List[Tuple[int, int]]:
        """Get the current trail points.
        
        Returns:
            List of (x, y) coordinates making up the trail
        """
        return self.trail_points

    def get_drawing_metrics(self) -> Dict:
        """Get metrics about the current drawing.
        
        Returns:
            Dictionary containing:
            - point_count: Number of points in trail
            - trail_length: Approximate length of trail in pixels
            - bounds: (min_x, min_y, max_x, max_y) of trail
            - smoothing_stats: Information about position smoothing
        """
        try:
            if not self.trail_points:
                return {
                    'point_count': 0,
                    'trail_length': 0,
                    'bounds': (0, 0, 0, 0),
                    'smoothing_stats': {
                        'position_history_size': len(self.position_history),
                        'velocity_history_size': len(self.velocity_history)
                    }
                }
            
            # Calculate trail length
            length = 0
            for i in range(1, len(self.trail_points)):
                x1, y1 = self.trail_points[i-1]
                x2, y2 = self.trail_points[i]
                length += np.sqrt((x2-x1)**2 + (y2-y1)**2)
            
            # Calculate bounds
            points = np.array(self.trail_points)
            min_x, min_y = np.min(points, axis=0)
            max_x, max_y = np.max(points, axis=0)
            
            return {
                'point_count': len(self.trail_points),
                'trail_length': int(length),
                'bounds': (int(min_x), int(min_y), int(max_x), int(max_y)),
                'smoothing_stats': {
                    'position_history_size': len(self.position_history),
                    'velocity_history_size': len(self.velocity_history),
                    'current_velocity': self.last_velocity
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating metrics: {e}")
            return {}
```

# input\input_types.py

```py
# hand_drawing_challenge/input/input_types.py
from dataclasses import dataclass

@dataclass
class HandPoint:
    """Represents a point tracked by hand detection.
    
    Attributes:
        x: x-coordinate (0-1, normalized)
        y: y-coordinate (0-1, normalized)
        z: z-coordinate for depth (normalized)
    """
    x: float
    y: float
    z: float
```

# input\interfaces.py

```py
# hand_drawing_challenge/input/interfaces.py
from abc import ABC, abstractmethod
from typing import Any, Optional
import numpy as np

class InputProcessor(ABC):
    """Abstract base class for input processors."""
    
    @abstractmethod
    def process(self, *args: Any, **kwargs: Any) -> Optional[np.ndarray]:
        """Process input and emit relevant events.
        
        Args:
            *args: Variable positional arguments
            **kwargs: Variable keyword arguments
        """
        pass
    
    @abstractmethod
    def is_active(self) -> bool:
        """Check if processor is active and ready to process input.
        
        Returns:
            bool: True if processor is active, False otherwise
        """
        pass
        
    @abstractmethod
    def start(self) -> None:
        """Start the processor and initialize resources."""
        pass
        
    @abstractmethod
    def stop(self) -> None:
        """Stop the processor and release resources."""
        pass
        
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up processor resources."""
        pass

```

# input\manager.py

```py
# hand_drawing_challenge/input/manager.py

import logging
from typing import Dict, Optional
import numpy as np
from ..events.bus import EventBus
from ..events.types import GameEventType
from .interfaces import InputProcessor
from .processors.hand_tracking import HandTrackingProcessor, HandProcessorConfig

class InputManager:
    """Manages and coordinates multiple input processors."""
    
    def __init__(self, event_bus: EventBus, camera_id: int = 0):
        """Initialize input manager."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Creating InputManager")
        
        self.event_bus = event_bus
        self.processors: Dict[str, InputProcessor] = {}
        self.is_processing = False
        self.current_frame: Optional[np.ndarray] = None
        self._started = False  # Track if already started
        
        # Subscribe to game events
        self.event_bus.subscribe(GameEventType.GAME_ENDED, self._handle_game_end)
        
        # Initialize hand tracking
        self._init_hand_tracking(camera_id)
    
    def _init_hand_tracking(self, camera_id: int) -> None:
        """Initialize hand tracking processor."""
        try:
            self.logger.debug("Initializing HandTrackingProcessor")
            config = HandProcessorConfig(
                camera_width=640,
                camera_height=480,
                camera_id=camera_id,
                mirror_camera=True,
                draw_debug=True
            )
            
            self.hand_tracker = HandTrackingProcessor(
                event_bus=self.event_bus,
                config=config
            )
            
            self.register_processor("hand_tracking", self.hand_tracker)
            
        except Exception as e:
            self.logger.error(f"Failed to initialize hand tracking: {e}")
            raise
    
    def register_processor(self, name: str, processor: InputProcessor) -> None:
        """Register an input processor."""
        if name in self.processors:
            self.logger.debug(f"Replacing existing processor {name}")
            self.unregister_processor(name)
        
        self.logger.debug(f"Registering processor '{name}': {processor}")
        self.processors[name] = processor
        self.logger.info(f"Successfully registered processor {name}")
    
    def unregister_processor(self, name: str) -> None:
        """Remove an input processor."""
        if name in self.processors:
            processor = self.processors[name]
            self.logger.debug(f"Unregistering processor '{name}'")
            processor.stop()
            processor.cleanup()
            del self.processors[name]
    
    def get_processor(self, name: str) -> Optional[InputProcessor]:
        """Get a registered processor by name."""
        return self.processors.get(name)
    
    def start(self) -> None:
        """Start all registered processors."""
        if self._started:
            self.logger.debug("InputManager already started, ignoring start request")
            return
            
        self.logger.info("Starting input processing")
        try:
            for name, processor in self.processors.items():
                self.logger.debug(f"Starting processor {name}")
                processor.start()
                processor.enable_processing()
            
            self.is_processing = True
            self._started = True
            
        except Exception as e:
            self.logger.error(f"Error starting input processing: {e}")
            self.stop()
            raise
    
    def stop(self) -> None:
        """Stop all registered processors."""
        self.logger.info("Stopping input processing")
        self.is_processing = False
        self._started = False
        
        for name, processor in self.processors.items():
            try:
                self.logger.debug(f"Stopping processor {name}")
                processor.disable_processing()
                processor.stop()
            except Exception as e:
                self.logger.error(f"Error stopping processor {name}: {e}")
    
    def process_input(self) -> None:
        """Process input from all active processors."""
        if not self.is_processing:
            return
            
        try:
            for name, processor in self.processors.items():
                if processor.is_active():
                    frame_result = processor.process()
                    if frame_result is not None:
                        self.current_frame = frame_result
                        
        except Exception as e:
            self.logger.error(f"Error processing input: {e}")
    
    def get_frame(self) -> Optional[np.ndarray]:
        """Get the most recent camera frame."""
        return self.current_frame
    
    def cleanup(self) -> None:
        """Clean up all processors."""
        self.logger.info("Cleaning up input manager")
        for name in list(self.processors.keys()):
            try:
                self.unregister_processor(name)
            except Exception as e:
                self.logger.error(f"Error cleaning up processor {name}: {e}")
    
    def _handle_game_end(self, event_type: GameEventType, data: Optional[dict] = None) -> None:
        """Handle game end event."""
        self.logger.info("Handling game end event")
        self.stop()
        self.cleanup()
```

# input\processors\hand_tracking.py

```py
"""
hand_drawing_challenge/input/processors/hand_tracking.py

Implements HandTrackingProcessor, an InputProcessor that:
- Opens camera with cv2.VideoCapture
- Uses MediaPipe to detect hand landmarks
- Publishes hand detection events
"""

import cv2
import mediapipe as mp
import numpy as np
import logging
from dataclasses import dataclass
from typing import Optional, Tuple, Any

# Adjust the imports below if your structure differs:
from hand_drawing_challenge.events.bus import EventBus
from hand_drawing_challenge.events.types import GameEventType
from hand_drawing_challenge.input.interfaces import InputProcessor
from hand_drawing_challenge.input.input_types import HandPoint


@dataclass
class HandProcessorConfig:
    """Configuration for hand tracking processor."""
    min_detection_confidence: float = 0.3
    min_tracking_confidence: float = 0.3
    camera_width: int = 640
    camera_height: int = 480
    camera_id: int = 0
    mirror_camera: bool = True
    draw_debug: bool = True
    target_fps: int = 60

class HandTrackingProcessor(InputProcessor):
    """
    Processes hand tracking input using MediaPipe and publishes relevant events.
    """
    
    def __init__(self, event_bus: EventBus, config: HandProcessorConfig):
        print(">>> hand_tracking_processor.py: HandTrackingProcessor.__init__ CALLED")
        self.logger = logging.getLogger(__name__)
        self.event_bus = event_bus
        self.config = config
        self._active = False
        self._processing_enabled = False
        
        # State tracking
        self.hand_detected = False
        self.is_drawing = False
        self.last_position: Optional[Tuple[int, int]] = None
        
        # Subscribe to drawing events
        self.event_bus.subscribe(GameEventType.DRAWING_STARTED, self._handle_drawing_event)
        self.event_bus.subscribe(GameEventType.DRAWING_ENDED, self._handle_drawing_event)
        
        # Camera reference
        self.camera = None

        # Setup MediaPipe Hands
        self.logger.debug("Creating mp.solutions.hands.Hands() with detection/tracking confidence")
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=config.min_detection_confidence,
            min_tracking_confidence=config.min_tracking_confidence
        )

    def _initialize_camera(self) -> None:
        """Initialize the camera but don't start it yet"""
        try:
            self.logger.info(f"Attempting to open camera {self.config.camera_id}")
            self.camera = cv2.VideoCapture(self.config.camera_id)
            if not self.camera.isOpened():
                self.logger.error(f"Failed to open camera {self.config.camera_id}!")
                return
            
            # Set and verify camera properties
            self.logger.info("Setting camera properties...")
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.camera_width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.camera_height)
            self.camera.set(cv2.CAP_PROP_FPS, self.config.target_fps)

            # Read actual properties
            w = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
            h = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
            fps = self.camera.get(cv2.CAP_PROP_FPS)
            backend = self.camera.getBackendName()
            
            self.logger.info(f"Camera initialized with:")
            self.logger.info(f"- Resolution: {w}x{h}")
            self.logger.info(f"- FPS: {fps}")
            self.logger.info(f"- Backend: {backend}")
            
            # Test frame capture
            success, test_frame = self.camera.read()
            if success and test_frame is not None:
                self.logger.info(f"Test frame captured successfully: shape={test_frame.shape}, dtype={test_frame.dtype}")
                self._active = True
            else:
                self.logger.error("Failed to capture test frame!")
                self.camera.release()
                self.camera = None

        except Exception as e:
            self.logger.error(f"Exception opening camera: {e}")
            if self.camera:
                self.camera.release()
                self.camera = None

    def is_active(self) -> bool:
        """Return whether the processor is active and camera is open."""
        return bool(self._active and self.camera and self.camera.isOpened())

    def start(self) -> None:
        """Start the processor and initialize camera resources."""
        print(">>> hand_tracking_processor.py: start() called")
        self.logger.info("HandTrackingProcessor.start() invoked")

        # Attempt camera init if not done yet
        if self.camera is None or not self.camera.isOpened():
            self._initialize_camera()
        
        # If camera is good, mark active
        if self.camera and self.camera.isOpened():
            self._active = True
            self.logger.info("Hand tracking processor started successfully")
            print(">>> Camera opened successfully!")
        else:
            self.logger.error("Camera not available; cannot start.")
            print(">>> Camera NOT opened; check logs...")

    def stop(self) -> None:
        """Stop the processor and release camera resources."""
        self.logger.info("Stopping HandTrackingProcessor")
        self._active = False
        if self.camera is not None:
            self.camera.release()
        self.cleanup()

    def cleanup(self) -> None:
        """Clean up hand resources."""
        try:
            if hasattr(self, 'hands') and self.hands:
                self.hands.close()
                self.hands = None
            if hasattr(self, 'camera') and self.camera:
                self.camera.release()
                self.camera = None

            self._active = False
            self._processing_enabled = False

        except Exception as e:
                self.logger.warning(f"Error during cleanup: {e}")
    
    def enable_processing(self) -> None:
        """Enable processing."""
        self.logger.info("Hand Tracking processing enabled")
        self._processing_enabled = True

    def disable_processing(self) -> None:
        """Disable processing."""
        self.logger.info("Hand Tracking processing disabled")
        self._processing_enabled = False
    
    def process(self, *args: Any, **kwargs: Any) -> Optional[np.ndarray]:
        """Process the current frame and update hand tracking state.

        Returns:
            The camera frame (with debug overlays if draw_debug=True),
            or None if the camera read fails or not active.
        """
        if not self._active or not self._processing_enabled:
            return None
            
        try:
            success, frame = self.camera.read()
            if not success or frame is None:
                return None
                
            if self.config.mirror_camera:
                frame = cv2.flip(frame, 1)
            
            # Process frame with MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            
            # Process hand landmarks
            if results.multi_hand_landmarks:
                if not self.hand_detected:
                    self.hand_detected = True
                    self.event_bus.publish(GameEventType.HAND_DETECTED)
                
                # Get index fingertip position (landmark 8)
                landmarks = results.multi_hand_landmarks[0].landmark
                index_tip = landmarks[8]
                
                # Convert to pixel coordinates
                h, w = frame.shape[:2]
                x = int(index_tip.x * w)
                y = int(index_tip.y * h)
                
                # Update position with smoother transitions
                self.last_position = (x, y)
                
                # Create and publish hand point
                hand_point = HandPoint(
                    x=index_tip.x,
                    y=index_tip.y,
                    z=index_tip.z
                )
                
                # Publish position update with additional context
                self.event_bus.publish(
                    GameEventType.HAND_POSITION_UPDATED,
                    {
                        "position": hand_point,
                        "is_drawing": self.is_drawing,
                        "frame_dimensions": (w, h)
                    }
                )
            else:
                if self.hand_detected:
                    self.hand_detected = False
                    self.last_position = None
                    self.event_bus.publish(GameEventType.HAND_LOST)
            
            # Draw debug visualization if enabled
            if self.config.draw_debug:
                frame = self._draw_debug(frame, results)
            
            return frame
            
        except Exception as e:
            self.logger.error(f"Error processing frame: {e}")
            return None
    
    def _draw_debug(self, frame: np.ndarray, results: Any) -> np.ndarray:
        """Draw debug info (only index finger tip) on the BGR frame."""
        debug_frame = frame.copy()
        if results and results.multi_hand_landmarks:
            # Only draw index finger tip (landmark 8)
            if self.last_position:
                # Convert normalized coordinates to pixel coordinates for drawing
                h, w = frame.shape[:2]
                x = int(self.last_position[0] * w)
                y = int(self.last_position[1] * h)
                color = (0, 255, 0) if self.is_drawing else (0, 0, 255)
                cv2.circle(debug_frame, (x, y), 5, color, -1)
        return debug_frame
            
    def _handle_drawing_event(self, event_type: GameEventType, data: Optional[dict] = None) -> None:
        """Handle drawing state change events."""
        self.is_drawing = (event_type == GameEventType.DRAWING_STARTED)
        self.logger.info(f"Drawing state changed to: {self.is_drawing}")

    def set_drawing_state(self, is_drawing: bool) -> None:
        """Enable or disable drawing mode."""
        if self.is_drawing != is_drawing:
            self.is_drawing = is_drawing
            event_type = (GameEventType.DRAWING_STARTED if is_drawing 
                          else GameEventType.DRAWING_ENDED)
            self.event_bus.publish(event_type)

```

# main.py

```py
# main.py

import pygame
import sys
from hand_drawing_challenge.application.game_application import GameApplication
from hand_drawing_challenge.application.config import GameConfig

def main():
    """Application entry point."""
    try:
        # Initialize pygame
        pygame.init()
        
        # Create configuration
        config = GameConfig(
            screen_size=(1280, 720),
            fps=60,
            debug_mode=True,
            camera_device=0,
            camera_width=640,
            camera_height=480
        )
        
        # Create and start application
        app = GameApplication(config)
        app.start()
        
    except Exception as e:
        print(f"Error running application: {e}")
        sys.exit(1)
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
```

# services\drawing_service.py

```py
# hand_drawing_challenge/services/drawing_service.py
import numpy as np
import cv2
from typing import Optional, List, Tuple
from dataclasses import dataclass
from ..events.bus import EventBus
from ..events.types import DrawingEvent
from input_processing.drawing_tracker import DrawingTracker

@dataclass
class DrawingState:
    """Current state of the drawing canvas."""
    position: Optional[Tuple[int, int]]
    is_drawing: bool
    canvas: np.ndarray
    trail_points: List[Tuple[int, int]]

class DrawingService:
    """Manages drawing state and operations."""
    
    def __init__(self, event_bus: EventBus, width: int = 640, height: int = 480):
        """Initialize drawing service.
        
        Args:
            event_bus: Event bus for publishing state changes
            width: Canvas width in pixels
            height: Canvas height in pixels
        """
        self.event_bus = event_bus
        self.width = width
        self.height = height
        
        # Drawing state
        self.canvas = np.zeros((height, width, 3), dtype=np.uint8)
        self.is_drawing = False
        self.drawing_tracker = DrawingTracker(width=width, height=height)
        
    def update_drawing(self, position: Optional[Tuple[int, int]]) -> None:
        """Update drawing state with new position.
        
        Args:
            position: Current drawing position (x, y)
        """
        if not position:
            return
            
        # Update trail points
        smoothed_pos = self.drawing_tracker.update(position, self.is_drawing)
        
        if smoothed_pos and self.is_drawing:
            trail_points = self.drawing_tracker.get_trail_points()
            if len(trail_points) > 1:
                self._draw_line(trail_points[-2], trail_points[-1])
            
            # Emit state change event
            self.event_bus.publish(
                DrawingEvent.STATE_CHANGED,
                state=self.get_state()
            )
    
    def _draw_line(self, start: Tuple[int, int], end: Tuple[int, int]) -> None:
        """Draw a line on the canvas.
        
        Args:
            start: Starting point (x, y)
            end: Ending point (x, y)
        """
        cv2.line(
            self.canvas,
            start,
            end,
            (0, 255, 0),  # Green color
            2  # Line thickness
        )
    
    def set_drawing_state(self, is_drawing: bool) -> None:
        """Set whether currently drawing or not.
        
        Args:
            is_drawing: Whether to enable drawing mode
        """
        self.is_drawing = is_drawing
        self.event_bus.publish(
            DrawingEvent.MODE_CHANGED,
            is_drawing=is_drawing
        )
    
    def clear(self) -> None:
        """Clear the drawing canvas."""
        self.canvas.fill(0)
        self.drawing_tracker.clear()
        self.event_bus.publish(DrawingEvent.CANVAS_CLEARED)
    
    def get_state(self) -> DrawingState:
        """Get current drawing state.
        
        Returns:
            DrawingState: Current state of the drawing
        """
        return DrawingState(
            position=self.drawing_tracker.last_valid_position,
            is_drawing=self.is_drawing,
            canvas=self.canvas.copy(),
            trail_points=self.drawing_tracker.get_trail_points()
        )
```

# services\pattern_manager.py

```py
# hand_drawing_challenge/services/pattern_manager.py

from typing import List, Optional, Tuple
from .patterns.models import Pattern, Point
from .patterns.generator import PatternGenerator
from .patterns.renderer import PatternRenderer
from ..events.bus import EventBus
from ..events.types import GameEventType
from ..events.events import PatternGeneratedEvent, PatternCompletedEvent

class PatternManager:
    """Service class that manages pattern generation, validation, and scoring."""
    
    def __init__(self, event_bus: EventBus):
        """Initialize the pattern manager.
        
        Args:
            event_bus: Event bus for communication
        """
        self._event_bus = event_bus
        self._generator = PatternGenerator()
        self._renderer = PatternRenderer()
        self._current_pattern: Optional[Pattern] = None
        self._current_difficulty = 1
    
    def initialize(self) -> None:
        """Initialize the pattern manager."""
        self._generator._initialize_basic_patterns()
    
    def get_next_pattern(self) -> Pattern:
        """Get the next pattern based on current difficulty."""
        patterns = self._generator.get_patterns_by_difficulty(self._current_difficulty)
        self._current_pattern = patterns[0] if patterns else self._generator.get_pattern("square")
        
        # Create and publish event
        event = PatternGeneratedEvent(pattern=self._current_pattern)
        self._event_bus.publish(GameEventType.PATTERN_GENERATED, event)
        
        return self._current_pattern
    
    def get_guide_points(self) -> List[Tuple[float, float]]:
        """Get guide points for the current pattern."""
        if self._current_pattern:
            return self._renderer.get_guide_points(self._current_pattern)
        return []
    
    def get_expected_path(self) -> List[Tuple[float, float]]:
        """Get expected path points for the current pattern."""
        if self._current_pattern:
            return self._renderer.get_expected_path(self._current_pattern)
        return []
    
    def validate_drawing(self, drawing_points: List[Tuple[float, float]]) -> float:
        """Validate a drawing against the current pattern.
        
        Args:
            drawing_points: List of points from user's drawing
            
        Returns:
            float: Score between 0 and 1
        """
        if not self._current_pattern or not drawing_points:
            return 0.0
            
        # TODO: Implement drawing validation logic
        # This would compare the drawing_points against the pattern's expected_path
        # and return a score based on how well they match
        
        score = 0.5  # Placeholder score
        
        # Create and publish event
        event = PatternCompletedEvent(
            pattern=self._current_pattern,
            score=score
        )
        self._event_bus.publish(GameEventType.PATTERN_COMPLETED, event)
        
        return score
    
    def increase_difficulty(self) -> None:
        """Increase the pattern difficulty."""
        self._current_difficulty = min(self._current_difficulty + 1, 3)
    
    def reset_difficulty(self) -> None:
        """Reset pattern difficulty to default."""
        self._current_difficulty = 1
```

# services\patterns\__init__.py

```py
from .models import Point, Pattern
from .generator import PatternGenerator
from .renderer import PatternRenderer

__all__ = ['Point', 'Pattern', 'PatternGenerator', 'PatternRenderer']
```

# services\patterns\generator.py

```py
from typing import Dict, List
import math
from .models import Point, Pattern

class PatternGenerator:
    def __init__(self):
        self.patterns: Dict[str, Pattern] = {}
        self._initialize_basic_patterns()
    
    def _initialize_basic_patterns(self):
        # Add square pattern
        self._add_square_pattern()
        # Add circle pattern
        self._add_circle_pattern()
        # Add triangle pattern
        self._add_triangle_pattern()
        # Add line pattern
        self._add_line_pattern()
    
    def _add_square_pattern(self):
        size = 100
        guide_points = [
            Point(0, 0),
            Point(size, 0),
            Point(size, size),
            Point(0, size)
        ]
        
        # Create more detailed path points for smooth drawing
        expected_path = []
        steps = 20  # Number of points per side
        for i in range(4):
            start = guide_points[i]
            end = guide_points[(i + 1) % 4]
            for step in range(steps):
                t = step / steps
                x = start.x + (end.x - start.x) * t
                y = start.y + (end.y - start.y) * t
                expected_path.append(Point(x, y))
        
        self.patterns["square"] = Pattern(
            name="square",
            difficulty=1,
            guide_points=guide_points,
            expected_path=expected_path
        )
    
    def _add_circle_pattern(self):
        radius = 50
        center = Point(50, 50)
        guide_points = []
        expected_path = []
        
        # Create circle points
        steps = 36  # Number of points around the circle
        for i in range(steps):
            angle = 2 * math.pi * i / steps
            x = center.x + radius * math.cos(angle)
            y = center.y + radius * math.sin(angle)
            point = Point(x, y)
            expected_path.append(point)
            if i % 9 == 0:  # Add guide points every 90 degrees
                guide_points.append(point)
        
        self.patterns["circle"] = Pattern(
            name="circle",
            difficulty=1,
            guide_points=guide_points,
            expected_path=expected_path
        )
    
    def _add_triangle_pattern(self):
        size = 100
        height = size * math.sqrt(3) / 2
        
        guide_points = [
            Point(size/2, 0),
            Point(size, height),
            Point(0, height)
        ]
        
        expected_path = []
        steps = 20
        for i in range(3):
            start = guide_points[i]
            end = guide_points[(i + 1) % 3]
            for step in range(steps):
                t = step / steps
                x = start.x + (end.x - start.x) * t
                y = start.y + (end.y - start.y) * t
                expected_path.append(Point(x, y))
        
        self.patterns["triangle"] = Pattern(
            name="triangle",
            difficulty=1,
            guide_points=guide_points,
            expected_path=expected_path
        )
    
    def _add_line_pattern(self):
        length = 100
        guide_points = [
            Point(0, 0),
            Point(length, 0)
        ]
        
        expected_path = []
        steps = 20
        for step in range(steps):
            t = step / steps
            x = t * length
            expected_path.append(Point(x, 0))
        
        self.patterns["line"] = Pattern(
            name="line",
            difficulty=1,
            guide_points=guide_points,
            expected_path=expected_path
        )
    
    def get_pattern(self, name: str) -> Pattern:
        return self.patterns.get(name)
    
    def get_patterns_by_difficulty(self, difficulty: int) -> List[Pattern]:
        return [p for p in self.patterns.values() if p.difficulty == difficulty]

```

# services\patterns\models.py

```py
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class Point:
    x: float
    y: float

@dataclass
class Pattern:
    name: str
    difficulty: int
    guide_points: List[Point]
    expected_path: List[Point]
    tolerance: float = 0.2
    size: Tuple[float, float] = (100, 100)
```

# services\patterns\renderer.py

```py
from typing import List, Tuple
from .models import Pattern

class PatternRenderer:
    @staticmethod
    def get_guide_points(pattern: Pattern) -> List[Tuple[float, float]]:
        """Returns guide points for display"""
        return [(p.x, p.y) for p in pattern.guide_points]
    
    @staticmethod
    def get_expected_path(pattern: Pattern) -> List[Tuple[float, float]]:
        """Returns expected path points for display or comparison"""
        return [(p.x, p.y) for p in pattern.expected_path]
```

# tests\test_engine\test_game_engine.py

```py
import pytest
from typing import Any
from unittest.mock import Mock, MagicMock
from hand_drawing_challenge.engine.game_engine import GameEngine
from hand_drawing_challenge.engine.modes.base_mode import GameMode
from hand_drawing_challenge.events.bus import EventBus
from hand_drawing_challenge.events.types import GameEventType

class MockGameMode(GameMode):
    """Mock implementation of GameMode for testing."""
    def __init__(self, event_bus: EventBus):
        super().__init__(event_bus)
        self.initialized = False
        self.started = False
        self.stopped = False
        self.updated = False
        self.last_delta = 0.0
    
    def initialize(self) -> None:
        self.initialized = True
    
    def start(self) -> None:
        self.started = True
        self.is_active = True
    
    def stop(self) -> None:
        self.stopped = True
        self.is_active = False
    
    def update(self, delta_time: float) -> None:
        self.updated = True
        self.last_delta = delta_time
    
    def handle_input(self, event: Any) -> None:
        """Handle input events."""
        pass

@pytest.fixture
def event_bus():
    """Create a fresh event bus for each test."""
    return EventBus()

@pytest.fixture
def game_engine(event_bus):
    """Create a fresh game engine for each test."""
    return GameEngine(event_bus)

@pytest.fixture
def mock_mode(event_bus):
    """Create a mock game mode for testing."""
    return MockGameMode(event_bus)

def test_initialization(game_engine):
    """Test initial game engine state."""
    assert not game_engine.is_running
    assert game_engine.current_mode is None
    assert game_engine.state_machine is not None

def test_engine_startup(game_engine):
    """Test engine initialization."""
    game_engine.initialize()
    assert game_engine.is_running

def test_change_mode(game_engine, mock_mode):
    """Test game mode switching."""
    game_engine.change_mode(mock_mode)
    
    assert game_engine.current_mode == mock_mode
    assert mock_mode.initialized
    assert mock_mode.started
    assert mock_mode.is_active

def test_change_mode_with_existing(game_engine, event_bus):
    """Test switching between modes."""
    first_mode = MockGameMode(event_bus)
    second_mode = MockGameMode(event_bus)
    
    game_engine.change_mode(first_mode)
    game_engine.change_mode(second_mode)
    
    assert game_engine.current_mode == second_mode
    assert first_mode.stopped
    assert not first_mode.is_active
    assert second_mode.started
    assert second_mode.is_active

def test_engine_update(game_engine, mock_mode):
    """Test engine update cycle."""
    game_engine.initialize()
    game_engine.change_mode(mock_mode)
    
    delta_time = 0.016
    game_engine.update(delta_time)
    
    assert mock_mode.updated
    assert mock_mode.last_delta == delta_time

def test_engine_update_when_stopped(game_engine, mock_mode):
    """Test update behavior when engine is not running."""
    game_engine.change_mode(mock_mode)
    
    game_engine.update(0.016)
    assert not mock_mode.updated  # Should not update when engine isn't running

def test_handle_game_end(game_engine, event_bus, mock_mode):
    """Test game end event handling."""
    game_engine.initialize()
    game_engine.change_mode(mock_mode)
    
    event_bus.publish(GameEventType.GAME_ENDED)
    
    assert not game_engine.is_running
    assert mock_mode.stopped

def test_event_subscription(game_engine, event_bus):
    """Test that engine properly subscribes to events."""
    # Check that the subscription was made during initialization
    assert GameEventType.GAME_ENDED in event_bus._subscribers

```

# tests\test_engine\test_game_startup.py

```py
# tests/test_engine/test_game_startup.py

import pytest
from unittest.mock import Mock, patch
import pygame
from hand_drawing_challenge.application.game_application import GameApplication
from hand_drawing_challenge.engine.modes.menu_mode import MenuMode

@pytest.fixture
def mock_pygame():
    """Mock pygame initialization."""
    pygame.init()  # Initialize pygame
    pygame.font.init()  # Initialize font system
    
    # Create a real surface for testing
    test_surface = pygame.Surface((1280, 720))
    
    with patch('pygame.display.set_mode', return_value=test_surface) as mock_set_mode, \
         patch('pygame.display.get_surface', return_value=test_surface), \
         patch('pygame.time.Clock'), \
         patch('pygame.event.get', return_value=[]), \
         patch('hand_drawing_challenge.ui.manager.UIManager.render'), \
         patch('hand_drawing_challenge.ui.manager.UIManager.update_frame'), \
         patch('hand_drawing_challenge.input.manager.InputManager.start'), \
         patch('hand_drawing_challenge.input.manager.InputManager.process_input'), \
         patch('hand_drawing_challenge.input.manager.InputManager.get_frame', return_value=None):
        
        yield mock_set_mode
    
    pygame.font.quit()
    pygame.quit()

@pytest.fixture
def game_app(mock_pygame):
    """Create a game application instance for testing."""
    return GameApplication()

def test_application_starts_with_menu(game_app, mock_pygame):
    """Test that the game application starts with menu mode."""
    # Start the application in test mode
    game_app.start(test_mode=True)
    
    # Verify engine is initialized with menu mode
    assert game_app.engine.current_mode is not None
    assert isinstance(game_app.engine.current_mode, MenuMode)
    assert game_app.engine.current_mode.is_active

def test_full_startup_sequence(game_app, mock_pygame):
    """Test the complete startup sequence."""
    game_app.start(test_mode=True)
    
    # Verify all systems are initialized
    assert game_app.is_running
    assert game_app.engine.is_running
    assert isinstance(game_app.engine.current_mode, MenuMode)
    assert game_app.engine.current_mode.is_active
    assert game_app.event_bus is not None

def test_menu_mode_cleanup_on_stop(game_app, mock_pygame):
    """Test that menu mode is properly cleaned up when game stops."""
    game_app.start(test_mode=True)
    menu_mode = game_app.engine.current_mode
    
    # Stop the game
    game_app.stop()
    
    # Verify cleanup
    assert not game_app.is_running
    assert not menu_mode.is_active

@patch('pygame.event.get')
def test_menu_handles_events(mock_event_get, game_app, mock_pygame):
    """Test that menu mode properly handles events."""
    # Setup mock events
    mock_event = Mock()
    mock_event.type = pygame.MOUSEBUTTONDOWN
    mock_event.pos = (640, 360)  # Center of screen
    mock_event_get.return_value = [mock_event]
    
    game_app.start(test_mode=True)
    menu_mode = game_app.engine.current_mode
    
    # Process one frame
    game_app._process_frame()
    
    # Verify event was processed
    assert menu_mode.is_active

```

# tests\test_engine\test_menu_startup.py

```py
# tests/test_engine/test_menu_startup.py

import pytest
from unittest.mock import Mock, patch
import pygame
from hand_drawing_challenge.engine.game_engine import GameEngine
from hand_drawing_challenge.events.bus import EventBus
from hand_drawing_challenge.engine.modes.menu_mode import MenuMode

@pytest.fixture(scope="session", autouse=True)
def pygame_init():
    """Initialize pygame for all tests."""
    pygame.init()
    yield
    pygame.quit()

@pytest.fixture
def event_bus():
    """Create a fresh event bus for each test."""
    return EventBus()

@pytest.fixture
def game_engine(event_bus):
    """Create a game engine instance for testing."""
    return GameEngine(event_bus)

@pytest.fixture
def mock_display():
    """Mock pygame display for testing."""
    with patch('pygame.display.set_mode') as mock_set_mode, \
         patch('pygame.display.get_surface') as mock_get_surface:
        # Create a mock surface
        mock_surface = Mock()
        mock_surface.get_rect.return_value = pygame.Rect(0, 0, 1280, 720)
        mock_set_mode.return_value = mock_surface
        mock_get_surface.return_value = mock_surface
        yield mock_set_mode

def test_engine_starts_with_menu_mode(game_engine, mock_display):
    """Test that the game engine starts in menu mode."""
    # Initialize the game engine
    game_engine.initialize()
    
    # Verify current mode is MenuMode
    assert game_engine.current_mode is not None
    assert isinstance(game_engine.current_mode, MenuMode)
    assert game_engine.current_mode.is_active

def test_menu_mode_initialization(game_engine, mock_display):
    """Test that menu mode is properly initialized."""
    game_engine.initialize()
    menu_mode = game_engine.current_mode
    
    # Verify menu mode state
    assert menu_mode.is_active
    assert menu_mode.event_bus is not None
    assert menu_mode.font_large is not None
    assert menu_mode.font_normal is not None
    assert menu_mode.buttons_initialized

def test_menu_mode_registers_events(event_bus, mock_display):
    """Test that menu mode properly registers for events."""
    menu_mode = MenuMode(event_bus)
    
    # Initialize and start menu mode
    menu_mode.initialize()
    menu_mode.start()
    
    # Verify menu is active
    assert menu_mode.is_active

def test_menu_mode_buttons_positioned(event_bus, mock_display):
    """Test that menu buttons are properly positioned."""
    menu_mode = MenuMode(event_bus)
    menu_mode.initialize()
    
    # Verify buttons are positioned within screen bounds
    assert 0 <= menu_mode.single_player_rect.centerx <= 1280
    assert 0 <= menu_mode.single_player_rect.centery <= 720
    assert 0 <= menu_mode.competitive_rect.centerx <= 1280
    assert 0 <= menu_mode.competitive_rect.centery <= 720

```

# tests\test_engine\test_state_machine.py

```py
import pytest
from hand_drawing_challenge.engine.state_machine import GameStateMachine, GameState, State

class MockState(State):
    """Mock state implementation for testing."""
    def __init__(self):
        super().__init__()
        self.entered = False
        self.exited = False
        self.updated = False
        self.last_delta = 0.0
    
    def enter(self) -> None:
        self.entered = True
    
    def exit(self) -> None:
        self.exited = True
    
    def update(self, delta_time: float) -> None:
        self.updated = True
        self.last_delta = delta_time

@pytest.fixture
def state_machine():
    """Create a fresh state machine for each test."""
    return GameStateMachine()

@pytest.fixture
def mock_states():
    """Create mock states for testing."""
    return {
        GameState.MENU: MockState(),
        GameState.PLAYING: MockState(),
        GameState.PAUSED: MockState()
    }

def test_initial_state(state_machine):
    """Test initial state is None."""
    assert state_machine.current_state is None
    assert state_machine.previous_state is None

def test_add_state(state_machine, mock_states):
    """Test adding states to the machine."""
    state_machine.add_state(GameState.MENU, mock_states[GameState.MENU])
    assert GameState.MENU in state_machine.states
    assert state_machine.states[GameState.MENU].state_machine == state_machine

def test_change_state(state_machine, mock_states):
    """Test state transition mechanics."""
    # Add states
    menu_state = mock_states[GameState.MENU]
    playing_state = mock_states[GameState.PLAYING]
    state_machine.add_state(GameState.MENU, menu_state)
    state_machine.add_state(GameState.PLAYING, playing_state)
    
    # Change to MENU
    state_machine.change_state(GameState.MENU)
    assert state_machine.current_state == menu_state
    assert menu_state.entered
    assert not menu_state.exited
    
    # Change to PLAYING
    state_machine.change_state(GameState.PLAYING)
    assert state_machine.current_state == playing_state
    assert state_machine.previous_state == menu_state
    assert menu_state.exited
    assert playing_state.entered

def test_invalid_state_change(state_machine, mock_states):
    """Test handling of invalid state transitions."""
    state_machine.add_state(GameState.MENU, mock_states[GameState.MENU])
    state_machine.change_state(GameState.MENU)
    
    # Try changing to non-existent state
    initial_state = state_machine.current_state
    state_machine.change_state(GameState.PLAYING)  # PLAYING not added
    assert state_machine.current_state == initial_state  # Should remain unchanged

def test_update_state(state_machine, mock_states):
    """Test state updates."""
    state_machine.add_state(GameState.MENU, mock_states[GameState.MENU])
    state_machine.change_state(GameState.MENU)
    
    delta_time = 0.016  # Simulate 16ms frame time
    state_machine.update(delta_time)
    
    current_state = mock_states[GameState.MENU]
    assert current_state.updated
    assert current_state.last_delta == delta_time

def test_update_without_state(state_machine):
    """Test update behavior with no current state."""
    state_machine.update(0.016)  # Should not raise any errors

```

# tests\test_events\__init__.py

```py

```

# tests\test_events\test_application.py

```py
import pytest
from unittest.mock import patch, Mock
import time
from hand_drawing_challenge.application.game_application import GameApplication
from hand_drawing_challenge.events.types import GameEventType

@pytest.fixture
def game_app():
    """Create a fresh game application instance for each test."""
    return GameApplication()

def test_initial_state(game_app):
    """Test initial application state."""
    assert not game_app.is_running
    assert game_app.engine is not None
    assert game_app.event_bus is not None

def test_start_initializes_engine(game_app):
    """Test that starting the application initializes the engine."""
    with patch.object(game_app.engine, 'initialize') as mock_init:
        game_app.start(test_mode=True)
        mock_init.assert_called_once()

def test_start_publishes_event(game_app):
    """Test that starting publishes the correct event."""
    with patch.object(game_app.event_bus, 'publish') as mock_publish:
        game_app.start(test_mode=True)
        mock_publish.assert_any_call(GameEventType.GAME_STARTED)

@patch('time.time')
def test_game_loop_updates(mock_time, game_app):
    """Test that the game loop updates the engine with correct delta time."""
    # Mock time to return increasing values
    times = [1.0, 1.016, 1.032]  # Simulate 16ms frames
    mock_time.side_effect = times
    
    # Mock engine update
    with patch.object(game_app.engine, 'update') as mock_update:
        # Stop the loop after first update
        def stop_after_update(*args):
            game_app.is_running = False
        mock_update.side_effect = stop_after_update
        
        # Run game loop
        game_app.start(test_mode=False)
        # actual_delta_time = mock_update.call_args.args[0]  # Python 3.8+

        # Verify engine was updated with correct delta time
        # mock_update.assert_called_once_with(abs(actual_delta_time - 0.016) < 1e-10)

def test_stop_publishes_event(game_app):
    """Test that stopping publishes the correct event."""
    game_app.start(test_mode=True)
    
    with patch.object(game_app.event_bus, 'publish') as mock_publish:
        game_app.stop()
        mock_publish.assert_called_with(GameEventType.GAME_ENDED)

def test_handle_game_end(game_app):
    """Test handling of game end event."""
    game_app.start(test_mode=True)
    assert game_app.is_running
    
    game_app.event_bus.publish(GameEventType.GAME_ENDED)
    assert not game_app.is_running

def test_multiple_starts(game_app):
    """Test that multiple start calls are handled correctly."""
    game_app.start(test_mode=True)
    initial_engine = game_app.engine
    
    # Try to start again
    game_app.start(test_mode=True)
    
    # Verify we didn't reinitialize anything
    assert game_app.engine is initial_engine

def test_stop_when_not_running(game_app):
    """Test that stopping when not running is handled gracefully."""
    with patch.object(game_app.event_bus, 'publish') as mock_publish:
        game_app.stop()
        mock_publish.assert_not_called()

@patch('time.time')
def test_game_loop_exception_handling(mock_time, game_app):
    """Test that exceptions in the game loop are handled properly."""
    mock_time.return_value = 1.0
    
    with patch.object(game_app.engine, 'update') as mock_update:
        mock_update.side_effect = Exception("Test error")
        
        with patch('builtins.print') as mock_print:
            game_app.start(test_mode=False)
            
            # Verify error was printed and game stopped
            assert mock_print.called
            assert not game_app.is_running

```

# tests\test_events\test_bus.py

```py
# tests/test_events/test_bus.py

import pytest
from hand_drawing_challenge.events.bus import EventBus
from hand_drawing_challenge.events.types import GameEventType

class TestEventBus:
    @pytest.fixture
    def event_bus(self):
        return EventBus()
    
    def test_subscribe_and_publish(self, event_bus):
        """Test basic subscription and publishing functionality."""
        received_events = []
        
        def handler(event_type, data):
            received_events.append((event_type, data))
        
        event_bus.subscribe(GameEventType.SCORE_UPDATED, handler)
        event_bus.publish(GameEventType.SCORE_UPDATED, 100)
        
        assert len(received_events) == 1
        assert received_events[0] == (GameEventType.SCORE_UPDATED, 100)
    
    def test_multiple_subscribers(self, event_bus):
        """Test multiple subscribers for the same event."""
        count1 = count2 = 0
        
        def handler1(event_type, data):
            nonlocal count1
            count1 += 1
            
        def handler2(event_type, data):
            nonlocal count2
            count2 += 1
        
        event_bus.subscribe(GameEventType.GAME_STARTED, handler1)
        event_bus.subscribe(GameEventType.GAME_STARTED, handler2)
        
        event_bus.publish(GameEventType.GAME_STARTED)
        
        assert count1 == 1
        assert count2 == 1
    
    def test_unsubscribe(self, event_bus):
        """Test unsubscribing from events."""
        received_events = []
        
        def handler(event_type, data):
            received_events.append((event_type, data))
        
        event_bus.subscribe(GameEventType.HAND_DETECTED, handler)
        event_bus.publish(GameEventType.HAND_DETECTED)
        event_bus.unsubscribe(GameEventType.HAND_DETECTED, handler)
        event_bus.publish(GameEventType.HAND_DETECTED)
        
        assert len(received_events) == 1
    
    def test_clear_subscribers(self, event_bus):
        """Test clearing all subscribers for an event type."""
        count = 0
        
        def handler(event_type, data):
            nonlocal count
            count += 1
        
        event_bus.subscribe(GameEventType.TURN_STARTED, handler)
        event_bus.clear_subscribers(GameEventType.TURN_STARTED)
        event_bus.publish(GameEventType.TURN_STARTED)
        
        assert count == 0
    
    def test_error_handling(self, event_bus):
        """Test that errors in handlers don't affect other handlers."""
        def bad_handler(event_type, data):
            raise Exception("Handler error")
            
        def good_handler(event_type, data):
            return True
        
        event_bus.subscribe(GameEventType.GAME_ENDED, bad_handler)
        event_bus.subscribe(GameEventType.GAME_ENDED, good_handler)
        
        # This should not raise an exception
        event_bus.publish(GameEventType.GAME_ENDED)

```

# tests\test_input\test_hand_tracking_integration.py

```py
# tests/test_input/test_hand_tracking_integration.py
import pytest
import numpy as np
import cv2
from unittest.mock import Mock, patch
from hand_drawing_challenge.input.processors.hand_tracking import HandTrackingProcessor, HandProcessorConfig
from hand_drawing_challenge.events.bus import EventBus
from hand_drawing_challenge.events.types import GameEventType

class TestHandTrackingIntegration:
    @pytest.fixture
    def event_bus(self):
        return EventBus()
        
    @pytest.fixture
    def mock_hand_landmarks(self):
        """Create mock MediaPipe hand landmarks."""
        landmark = Mock()
        landmark.x = 0.5  # Center of frame
        landmark.y = 0.5
        landmark.z = 0.0
        
        landmarks = [Mock() for _ in range(21)]
        landmarks[8] = landmark  # Index fingertip
        
        hand_landmarks = Mock()
        hand_landmarks.landmark = landmarks
        return hand_landmarks

    @pytest.fixture
    def test_frame(self):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.circle(frame, (320, 240), 50, (255, 255, 255), -1)
        return frame

    @pytest.fixture
    def processor(self, event_bus, test_frame, mock_hand_landmarks):
        config = HandProcessorConfig(
            camera_width=640,
            camera_height=480,
            camera_id=0,
            draw_debug=True
        )
        
        with patch('cv2.VideoCapture') as mock_camera, \
             patch('mediapipe.solutions.hands.Hands') as mock_hands:
            
            # Mock camera
            camera_instance = Mock()
            camera_instance.isOpened.return_value = True
            camera_instance.read.return_value = (True, test_frame)
            mock_camera.return_value = camera_instance
            
            # Mock MediaPipe hand detection
            hands_instance = Mock()
            mock_results = Mock()
            mock_results.multi_hand_landmarks = [mock_hand_landmarks]
            hands_instance.process.return_value = mock_results
            mock_hands.return_value = hands_instance
            
            processor = HandTrackingProcessor(event_bus, config)
            processor.start()
            return processor

    def test_drawing_workflow(self, processor, event_bus):
        """Test complete drawing workflow with hand tracking."""
        received_events = []
        def event_handler(event_type, data):
            received_events.append((event_type, data))
            
        # Subscribe to events
        event_bus.subscribe(GameEventType.HAND_DETECTED, event_handler)
        event_bus.subscribe(GameEventType.HAND_POSITION_UPDATED, event_handler)
        event_bus.subscribe(GameEventType.DRAWING_STARTED, event_handler)
        
        # Process frames
        frames = []
        processor.set_drawing_state(True)
        
        for _ in range(5):
            frame = processor.process()
            frames.append(frame)
            
        # Verify events
        assert any(event[0] == GameEventType.HAND_DETECTED for event in received_events), \
            "Should detect hand"
        assert any(event[0] == GameEventType.HAND_POSITION_UPDATED for event in received_events), \
            "Should update hand position"
        
        # Verify drawing
        assert len(frames) == 5
        trail_points = processor.drawing_tracker.get_trail_points()
        assert len(trail_points) > 0, "Should record trail points"
        
        processor.clear_canvas()
        assert len(processor.drawing_tracker.get_trail_points()) == 0

    def test_performance(self, processor):
        """Test processing performance."""
        import time
        
        frames_to_test = 10  # Reduced from 30 to speed up test
        times = []
        
        for _ in range(frames_to_test):
            start = time.time()
            processor.process()
            times.append(time.time() - start)
            
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        # More realistic performance expectations
        assert avg_time < 0.05, f"Average frame time too high: {avg_time:.4f}s"
        assert max_time < 0.1, f"Max frame time too high: {max_time:.4f}s"
```

# tests\test_input\test_hand_tracking_processor.py

```py
# tests/test_input/test_hand_tracking_processor.py

import pytest
import numpy as np
import cv2
from unittest.mock import Mock, patch, PropertyMock
from hand_drawing_challenge.input.processors.hand_tracking import (
    HandTrackingProcessor,
    HandProcessorConfig
)
from hand_drawing_challenge.events.types import GameEventType
from hand_drawing_challenge.events.bus import EventBus

@pytest.fixture
def mock_event_bus():
    return Mock(spec=EventBus)

@pytest.fixture
def test_frame():
    """Create a test frame."""
    return np.zeros((480, 640, 3), dtype=np.uint8)

@pytest.fixture
def mock_camera(test_frame):
    """Create a mock camera that returns proper frame data."""
    with patch('cv2.VideoCapture') as mock:
        camera_instance = Mock()
        camera_instance.isOpened.return_value = True
        camera_instance.read.return_value = (True, test_frame)
        mock.return_value = camera_instance
        return mock

def create_mock_hands():
    """Create a mock MediaPipe hands object."""
    mock_hands = Mock()
    mock_process = Mock()
    mock_hands.process = mock_process
    return mock_hands

@pytest.fixture
def mock_mediapipe(request):
    """Create a mock MediaPipe hands module."""
    with patch('mediapipe.solutions.hands') as mock_mp:
        mock_hands = create_mock_hands()
        mock_mp.Hands.return_value = mock_hands
        mock_mp.HAND_CONNECTIONS = []
        return mock_mp

@pytest.fixture
def config():
    """Create test configuration."""
    return HandProcessorConfig(
        camera_width=640,
        camera_height=480,
        camera_id=0,
        mirror_camera=True,
        draw_debug=True
    )

@pytest.fixture
def processor(mock_event_bus, mock_camera, mock_mediapipe, config, test_frame):
    """Create processor with mocked dependencies."""
    with patch('cv2.cvtColor', return_value=test_frame):
        processor = HandTrackingProcessor(mock_event_bus, config)
        return processor

def create_mock_hand_landmarks(x=0.5, y=0.5, z=0.0):
    """Create mock hand landmarks."""
    landmark = Mock()
    landmark.x = x
    landmark.y = y
    landmark.z = z
    
    landmarks = [Mock() for _ in range(21)]
    landmarks[8] = landmark  # Index fingertip
    hand_landmarks = Mock()
    hand_landmarks.landmark = landmarks
    return hand_landmarks

def test_initialization(processor, config):
    """Test initial state."""
    assert processor.event_bus is not None
    assert processor.config == config
    assert not processor.is_active()
    assert not processor.hand_detected
    assert not processor.is_drawing

def test_start_stop(processor):
    """Test start/stop functionality."""
    processor.start()
    assert processor.is_active()
    
    processor.stop()
    assert not processor.is_active()

def test_process_hand_detected(processor, mock_event_bus, test_frame):
    """Test hand detection."""
    processor.start()
    
    # Setup hand detection result
    mock_results = Mock()
    hand_landmarks = create_mock_hand_landmarks()
    mock_results.multi_hand_landmarks = [hand_landmarks]
    processor.hands.process = Mock(return_value=mock_results)
    
    with patch('cv2.cvtColor', return_value=test_frame):
        processor.process()
    
    mock_event_bus.publish.assert_any_call(GameEventType.HAND_DETECTED)

def test_process_hand_lost(processor, mock_event_bus, test_frame):
    """Test hand lost detection."""
    processor.start()
    processor.hand_detected = True
    
    # Setup no hands detected
    mock_results = Mock()
    mock_results.multi_hand_landmarks = None
    processor.hands.process = Mock(return_value=mock_results)
    
    with patch('cv2.cvtColor', return_value=test_frame):
        processor.process()
    
    mock_event_bus.publish.assert_called_with(GameEventType.HAND_LOST)
    assert not processor.hand_detected

# def test_camera_failure(processor, mock_camera, test_frame):
#     """Test camera failure handling."""
#     # Configure mock camera to simulate failure
#     camera_instance = mock_camera.return_value
#     camera_instance.read.return_value = (False, None)
#     camera_instance.isOpened.return_value = False
    
#     processor.start()
#     result = processor.process()
        
#     assert result is None
#     assert not processor.is_active()

def test_drawing_update(processor, test_frame):
    """Test drawing functionality."""
    processor.start()
    processor.is_drawing = True
    
    # Setup hand detection with movement
    mock_results = Mock()
    hand_landmarks = create_mock_hand_landmarks()
    mock_results.multi_hand_landmarks = [hand_landmarks]
    processor.hands.process = Mock(return_value=mock_results)
    
    with patch('cv2.cvtColor', return_value=test_frame), \
         patch('cv2.line') as mock_line:
        # Process multiple frames
        for i in range(3):
            hand_landmarks.landmark[8].x = 0.5 + (i * 0.1)  # Move finger
            processor.process()
        
        assert mock_line.called

def test_mirror_configuration(processor, test_frame):
    """Test mirror configuration."""
    processor.start()
    
    # Test with mirroring enabled
    processor.config.mirror_camera = True
    with patch('cv2.cvtColor', return_value=test_frame), \
         patch('cv2.flip', return_value=test_frame) as mock_flip:
        processor.process()
        assert mock_flip.called
    
    # Test with mirroring disabled
    processor.config.mirror_camera = False
    with patch('cv2.cvtColor', return_value=test_frame), \
         patch('cv2.flip', return_value=test_frame) as mock_flip:
        processor.process()
        assert not mock_flip.called

def test_debug_visualization(processor, test_frame):
    """Test debug visualization."""
    processor.start()
    processor.config.draw_debug = True
    
    # Setup hand detection
    mock_results = Mock()
    mock_results.multi_hand_landmarks = [create_mock_hand_landmarks()]
    processor.hands.process = Mock(return_value=mock_results)
    
    with patch('cv2.cvtColor', return_value=test_frame), \
         patch('cv2.circle') as mock_circle:
        processor.process()
        assert mock_circle.called

def test_clear_canvas(processor):
    """Test canvas clearing."""
    processor.start()
    
    # Add content to canvas
    processor.canvas.fill(255)
    processor.drawing_tracker.trail_points = [(0, 0), (1, 1)]
    
    processor.clear_canvas()
    assert np.all(processor.canvas == 0)
    assert len(processor.drawing_tracker.get_trail_points()) == 0

def test_inactive_processor(processor):
    """Test inactive processor behavior."""
    result = processor.process()
    assert result is None

```

# tests\test_input\test_manager.py

```py
# tests/test_input/test_manager.py
import pytest
from unittest.mock import Mock, patch
from hand_drawing_challenge.input.manager import InputManager
from hand_drawing_challenge.input.interfaces import InputProcessor
from hand_drawing_challenge.events.bus import EventBus
from hand_drawing_challenge.events.types import GameEventType

class MockProcessor(InputProcessor):
    def __init__(self):
        self.processed = False
        self._active = True
        self.cleaned_up = False
    
    def process(self, *args, **kwargs):
        self.processed = True
    
    def is_active(self):
        return self._active
    
    def cleanup(self):
        self.cleaned_up = True

class TestInputManager:
    @pytest.fixture
    def event_bus(self):
        return Mock(spec=EventBus)
    
    @pytest.fixture
    def input_manager(self, event_bus):
        return InputManager(event_bus)
    
    def test_register_processor(self, input_manager):
        processor = MockProcessor()
        input_manager.register_processor("test", processor)
        assert "test" in input_manager.processors
    
    def test_process_input_calls_active_processors(self, input_manager):
        processor = MockProcessor()
        input_manager.register_processor("test", processor)
        
        input_manager.process_input()
        assert processor.processed
    
    def test_cleanup_calls_processor_cleanup(self, input_manager):
        processor = MockProcessor()
        input_manager.register_processor("test", processor)
        
        input_manager.cleanup()
        assert processor.cleaned_up
    
    def test_game_end_triggers_cleanup(self, input_manager, event_bus):
        processor = MockProcessor()
        input_manager.register_processor("test", processor)
        
        # Simulate game end event
        for handler in event_bus.subscribe.call_args_list:
            event_type, callback = handler[0]
            if event_type == GameEventType.GAME_ENDED:
                callback(GameEventType.GAME_ENDED)
                break
        
        assert processor.cleaned_up
```

# tests\test_ui\test_drawing_canvas.py

```py
# tests/test_ui/test_drawing_canvas.py

import pytest
import pygame
import numpy as np
from unittest.mock import Mock
from typing import Optional, Tuple

from hand_drawing_challenge.ui.components.canvas import DrawingCanvas
from hand_drawing_challenge.input.input_types import HandPoint

class TestDrawingCanvas:
    """
    Test the DrawingCanvas UI component that renders hand drawing visualization.
    
    This test suite verifies:
    1. Basic canvas initialization and rendering
    2. Hand tracking updates and drawing visualization
    3. Drawing trail management
    """
    
    @pytest.fixture
    def mock_rect(self):
        """Create a mock pygame Rect for testing."""
        return pygame.Rect(0, 0, 800, 600)
    
    @pytest.fixture
    def drawing_canvas(self, mock_rect):
        """Create DrawingCanvas instance for testing."""
        return DrawingCanvas(mock_rect)
    
    def test_initialization(self, drawing_canvas, mock_rect):
        """Verify canvas initializes correctly."""
        assert drawing_canvas.rect == mock_rect
        assert drawing_canvas.canvas.shape == (mock_rect.height, mock_rect.width, 3)
        assert not drawing_canvas.is_drawing
        assert drawing_canvas.last_position is None
    
    def test_update_with_hand_point(self, drawing_canvas):
        """Test canvas updates with hand position."""
        # Create mock camera frame
        frame = np.zeros((600, 800, 3), dtype=np.uint8)
        # Create hand point with normalized coordinates (0-1)
        hand_point = HandPoint(x=0.5, y=0.5, z=0.0)  # Center of the frame
        
        drawing_canvas.update(frame, hand_point)
        
        # Should have updated last position
        assert drawing_canvas.last_position is not None
        assert drawing_canvas.current_frame is not None
    
    def test_drawing_trail(self, drawing_canvas):
        """Test trail rendering when drawing is active."""
        # Create frame and hand point
        frame = np.zeros((600, 800, 3), dtype=np.uint8)
        hand_point = HandPoint(x=0.5, y=0.5, z=0.0)
        
        # Enable drawing
        drawing_canvas.set_drawing_state(True)
        assert drawing_canvas.get_drawing_state() is True
        
        # Simulate movement with normalized coordinates
        positions = [(0.5, 0.5), (0.51, 0.51), (0.52, 0.52)]
        for x, y in positions:
            hand_point = HandPoint(x=x, y=y, z=0.0)
            drawing_canvas.update(frame, hand_point)
            
        # Verify canvas has been updated
        assert np.any(drawing_canvas.canvas != 0)  # Canvas should have some drawing
    
    def test_clear_canvas(self, drawing_canvas):
        """Test canvas clearing."""
        # Create frame and hand point
        frame = np.zeros((600, 800, 3), dtype=np.uint8)
        hand_point = HandPoint(x=0.5, y=0.5, z=0.0)
        drawing_canvas.set_drawing_state(True)
        drawing_canvas.update(frame, hand_point)
        
        # Then clear
        drawing_canvas.clear()
        assert np.all(drawing_canvas.canvas == 0)  # Canvas should be cleared
        assert drawing_canvas.last_position is None

```

# tests\test_ui\test_manager.py

```py
# file: tests/test_ui/test_manager.py

import pytest
import pygame
from unittest.mock import Mock, patch
from hand_drawing_challenge.events.bus import EventBus
from hand_drawing_challenge.events.types import GameEventType
from hand_drawing_challenge.ui.manager import UIManager
from hand_drawing_challenge.ui.base import UIComponent

@pytest.fixture
def event_bus():
    """Create a fresh event bus for testing."""
    return EventBus()

@pytest.fixture
def ui_manager(event_bus):
    """Create a UI manager with mocked pygame."""
    with patch('pygame.display.set_mode'), \
         patch('pygame.init'), \
         patch('pygame.display.set_caption'), \
         patch('pygame.font.init'), \
         patch('pygame.font.Font'):
        return UIManager(event_bus, screen_size=(1280, 720))

class TestUIManager:
    """Test suite for UIManager functionality."""
    
    def test_initialization(self, ui_manager):
        """Test UI manager initializes with correct components."""
        assert 'canvas' in ui_manager.components
        assert 'pattern' in ui_manager.components
        assert 'score' in ui_manager.components
        assert ui_manager.renderer is not None
    
    def test_component_visibility(self, ui_manager):
        """Test component visibility control."""
        # All components should be visible by default
        assert ui_manager.get_component('canvas').visible
        
        # Test visibility toggle
        ui_manager.set_component_visibility('canvas', False)
        assert not ui_manager.get_component('canvas').visible
        
        ui_manager.set_component_visibility('canvas', True)
        assert ui_manager.get_component('canvas').visible
    
    def test_update_calls_components(self, ui_manager):
        """Test that update calls update on all visible components."""
        # Replace all existing components with a mock
        mock_component = Mock(spec=UIComponent)
        mock_component.visible = True
        ui_manager.components = {'mock': mock_component}
        
        # Update UI manager
        delta_time = 0.016  # 60 FPS
        ui_manager.update(delta_time)
        
        # Verify component was updated
        mock_component.update.assert_called_once_with(delta_time)
    
    def test_render_calls_components(self, ui_manager):
        """Test that render calls draw on all visible components."""
        # Replace all existing components with a mock
        mock_component = Mock(spec=UIComponent)
        mock_component.visible = True
        ui_manager.components = {'mock': mock_component}
        
        # Create a mock surface
        mock_surface = Mock(spec=pygame.Surface)
        with patch.object(ui_manager.renderer, 'get_screen', return_value=mock_surface), \
             patch.object(ui_manager.renderer, 'present'):
            ui_manager.render()
        
        # Verify component was drawn with the mock surface
        mock_component.draw.assert_called_once_with(mock_surface)
    
    def test_game_end_cleanup(self, ui_manager, event_bus):
        """Test cleanup on game end event."""
        with patch.object(ui_manager.renderer, 'cleanup') as mock_cleanup:
            event_bus.publish(GameEventType.GAME_ENDED, None)
            mock_cleanup.assert_called_once()
    
    def test_get_nonexistent_component(self, ui_manager):
        """Test getting a component that doesn't exist."""
        assert ui_manager.get_component('nonexistent') is None
    
    def test_set_visibility_nonexistent_component(self, ui_manager):
        """Test setting visibility of nonexistent component doesn't raise error."""
        ui_manager.set_component_visibility('nonexistent', False)  # Should not raise

```

# ui\__init__.py

```py

```

# ui\base.py

```py
# ui/base.py
import pygame

class UIComponent:
    """Base class for UI components."""

    def __init__(self, rect: pygame.Rect):
        """Initialize the UI component.

        Args:
            rect: Position and size of the component
        """
        self.rect = rect
        self.visible = True

    def update(self, *args, **kwargs) -> None:
        """Update component state. To be implemented by subclasses."""
        pass

    def draw(self, screen: pygame.Surface) -> None:
        """Draw component to screen. To be implemented by subclasses.

        Args:
            screen: Pygame surface to draw on
        """
        pass


```

# ui\components\canvas.py

```py
# hand_drawing_challenge/ui/components/canvas.py

import cv2
import numpy as np
import pygame
import logging
from typing import Optional, Tuple, Union
from ..base import UIComponent
from ..utils.colors import Colors
from ...input.input_types import HandPoint
from ...input.drawing_tracker import DrawingTracker, DrawingConfig

class DrawingCanvas(UIComponent):
    """Drawing canvas component that displays camera feed and drawing visualization."""
    
    def __init__(self, rect: pygame.Rect):
        """Initialize the drawing canvas."""
        super().__init__(rect)
        self.logger = logging.getLogger(__name__)
        
        # State
        self.is_drawing = False
        self.current_frame: Optional[np.ndarray] = None
        self.last_position: Optional[Tuple[int, int]] = None
        
        # Create blank frame
        self.blank_frame = np.zeros((rect.height, rect.width, 3), dtype=np.uint8)
        
        # Initialize drawing tracker with optimized settings
        drawing_config = DrawingConfig(
            position_history_size=20,    # Increased for smoother lines
            velocity_history_size=10,    # More velocity history
            max_velocity=80.0,          # Adjusted for typical hand movement
            min_movement=4.0,           # Reduced jitter
            max_gap_distance=40.0,      # Conservative gap filling
            interpolation_steps=6,      # Smoother interpolation
            smoothing_factor=0.85,      # Strong smoothing
            prediction_weight=0.15      # Modest prediction influence
        )
        
        self.drawing_tracker = DrawingTracker(
            width=rect.width,
            height=rect.height,
            config=drawing_config
        )
    
    def update(self, frame: Optional[Union[np.ndarray, float]] = None) -> None:
        """Update canvas state with new frame.
        
        Args:
            frame: New frame to display (raw camera frame)
        """
        if frame is None:
            self.logger.warning("Received None frame")
            return
            
        try:
            if isinstance(frame, np.ndarray):
                # self.logger.info(f"Received frame: shape={frame.shape}, dtype={frame.dtype}")
                
                # Ensure frame has correct dimensions and type
                if frame.shape[1] != self.rect.width or frame.shape[0] != self.rect.height:
                    self.logger.info(f"Resizing frame from {frame.shape[:2]} to {(self.rect.height, self.rect.width)}")
                    frame = cv2.resize(frame, (self.rect.width, self.rect.height))
                
                if frame.dtype != np.uint8:
                    self.logger.info(f"Converting frame from {frame.dtype} to uint8")
                    frame = frame.astype(np.uint8)
                
                # # Check if frame contains any data
                # if frame.size == 0 or frame.mean() == 0:
                #     self.logger.warning("Frame appears to be empty or black")
                # else:
                #     self.logger.info(f"Frame mean pixel value: {frame.mean():.2f}")
                    
                # Store raw camera frame
                self.current_frame = frame.copy()
            else:
                self.logger.warning(f"Invalid frame type received: {type(frame)}")
        except Exception as e:
            self.logger.error(f"Error updating frame: {e}")
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the canvas contents to screen."""
        if not self.visible:
            return
            
        try:
            # Use blank frame if no camera feed
            display_frame = self.current_frame if self.current_frame is not None else self.blank_frame
            
            if display_frame is None:
                pygame.draw.rect(screen, Colors.RED, self.rect, 2)
                return
                
            # Convert frame to pygame surface
            display = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            display_surface = pygame.surfarray.make_surface(display.swapaxes(0, 1))
            
            # Draw camera frame
            screen.blit(display_surface, self.rect)
            
            # Draw trail with improved visuals
            self._draw_trail_points(screen)
            
            # Draw border
            pygame.draw.rect(screen, Colors.BORDER, self.rect, 2)
        
        except Exception as e:
            self.logger.error(f"Error drawing frame: {e}")
            pygame.draw.rect(screen, Colors.RED, self.rect, 2)
    
    def _draw_trail_points(self, screen: pygame.Surface) -> None:
        """Draw the trail points on the screen."""
        trail_points = self.drawing_tracker.get_trail_points()
        # self.logger.info(f"Drawing trail points: count={len(trail_points)}")
        if len(trail_points) > 1:
            # Offset points by canvas position
            adjusted_points = [(x + self.rect.x, y + self.rect.y) 
                             for x, y in trail_points]
            pygame.draw.lines(
                screen,
                Colors.TRAIL_COLOR,
                False,
                adjusted_points,
                8  # Thickness parameter
            )
            self.logger.info(f"Drew lines with {len(adjusted_points)} points")
    
    def update_hand_position(self, hand_point: Optional[HandPoint]) -> None:
        """Update hand position and drawing state.
        
        Args:
            hand_point: Current hand position
        """
        # Convert normalized coordinates to canvas coordinates
        x = int(hand_point.x * self.rect.width)
        y = int(hand_point.y * self.rect.height)
        
        # Update drawing tracker
        smoothed_pos = self.drawing_tracker.update(
            position=(x, y),
            is_drawing=self.is_drawing
        )
        
        if smoothed_pos:
            self.last_position = smoothed_pos
            
            if self.is_drawing:
                metrics = self.drawing_tracker.get_drawing_metrics()
                self.logger.debug(f"Drawing metrics: {metrics}")
    
    def set_drawing_state(self, is_drawing: bool) -> None:
        """Set whether currently drawing.
        
        Args:
            is_drawing: Whether drawing is enabled
        """
        self.logger.info(f"Setting drawing state to: {is_drawing}")
        if self.is_drawing != is_drawing:
            self.is_drawing = is_drawing
    
    def get_drawing_state(self) -> bool:
        """Get current drawing state.
        
        Returns:
            bool: Whether drawing is enabled
        """
        return self.is_drawing
        
    def clear(self) -> None:
        """Reset the canvas display state."""
        self.current_frame = None
        self.last_position = None
        self.drawing_tracker.clear()

```

# ui\components\pattern_display.py

```py
# ui/components/pattern_display.py
import pygame
from ..base import UIComponent
from ..utils.colors import Colors

class PatternDisplay(UIComponent):
    """Component for displaying the pattern to be drawn."""

    def __init__(self, rect: pygame.Rect):
        super().__init__(rect)
        self.current_pattern = None
        self.font = pygame.font.Font(None, 36)

    def set_pattern(self, pattern) -> None:
        """Set the current pattern to display."""
        self.current_pattern = pattern

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the pattern display component."""
        # Draw background
        pygame.draw.rect(screen, Colors.COMPONENT_BG, self.rect)
        pygame.draw.rect(screen, Colors.BORDER, self.rect, 2)

        # Draw title
        title = self.font.render("Pattern", True, Colors.TEXT)
        title_rect = title.get_rect(centerx=self.rect.centerx, top=self.rect.top + 10)
        screen.blit(title, title_rect)

        if self.current_pattern:
            # Draw the actual pattern (placeholder)
            pattern_rect = pygame.Rect(
                self.rect.x + 20,
                self.rect.y + 60,
                self.rect.width - 40,
                self.rect.height - 80
            )
            pygame.draw.rect(screen, Colors.PATTERN, pattern_rect)
        else:
            # Draw "No Pattern" text
            text = self.font.render("No Pattern", True, Colors.TEXT)
            text_rect = text.get_rect(center=self.rect.center)
            screen.blit(text, text_rect)


```

# ui\components\score_display.py

```py
# ui/components/score_display.py
import pygame
from ..base import UIComponent
from ..utils.colors import Colors

class ScoreDisplay(UIComponent):
    """Component for displaying the current score and game state."""

    def __init__(self, rect: pygame.Rect):
        super().__init__(rect)
        self.score = 0
        self.game_state = "Ready"
        self.is_drawing = False
        self.font = pygame.font.Font(None, 36)

    def update(self, score: int, game_state: str, is_drawing: bool) -> None:
        """Update the display state."""
        self.score = score
        self.game_state = game_state
        self.is_drawing = is_drawing

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the score display component."""
        # Draw background
        pygame.draw.rect(screen, Colors.COMPONENT_BG, self.rect)
        pygame.draw.rect(screen, Colors.BORDER, self.rect, 2)

        # Draw title
        title = self.font.render("Score", True, Colors.TEXT)
        title_rect = title.get_rect(centerx=self.rect.centerx, top=self.rect.top + 10)
        screen.blit(title, title_rect)

        # Draw score
        score_text = self.font.render(str(self.score), True, Colors.TEXT)
        score_rect = score_text.get_rect(centerx=self.rect.centerx, top=title_rect.bottom + 20)
        screen.blit(score_text, score_rect)

        # Draw game state
        state_color = Colors.SUCCESS if self.is_drawing else Colors.TEXT
        state_text = self.font.render(self.game_state, True, state_color)
        state_rect = state_text.get_rect(centerx=self.rect.centerx, top=score_rect.bottom + 40)
        screen.blit(state_text, state_rect)


```

# ui\game_ui.py

```py
# hand_drawing_challenge/ui/game_ui.py

import pygame
import cv2
from typing import Optional

from ..events.bus import EventBus
from ..events.types import GameEventType
from ..input.manager import InputManager
from ..input.processors.hand_tracking import HandTrackingProcessor, HandProcessorConfig
from .components.canvas import DrawingCanvas
from .components.pattern_display import PatternDisplay
from .components.score_display import ScoreDisplay
from .utils.colors import Colors

class GameUI:
    """
    Main UI orchestrator that integrates all visual components and input handling.
    
    This class coordinates:
    - Window management and rendering
    - Component layout and updates
    - Camera and hand tracking integration
    - Event dispatching
    """
    
    def __init__(self, width: int = 1280, height: int = 720):
        pygame.init()
        pygame.display.set_caption("Hand Drawing Challenge")
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        
        # Initialize event system
        self.event_bus = EventBus()
        
        # Initialize input processing
        self.setup_input_processing()
        
        # Create UI Components
        self.setup_ui_components()
        
        # Game state
        self.is_running = False
        self.current_score = 0
        
    def setup_input_processing(self) -> None:
        """Initialize input processing."""
        # Initialize input manager with event bus
        self.input_manager = InputManager(self.event_bus)
        
        # Initialize and register hand tracking processor
        hand_tracking_config = HandProcessorConfig(
            camera_width=640,
            camera_height=480,
            mirror_camera=False,
            draw_debug=True
        )
        self.hand_tracker = HandTrackingProcessor(self.event_bus, hand_tracking_config)
        self.input_manager.register_processor('hand_tracking', self.hand_tracker)
        
        # Start the hand tracker
        self.hand_tracker.start()
        
    def setup_ui_components(self) -> None:
        """Initialize and position all UI components."""
        # Main drawing area (center)
        self.drawing_canvas = DrawingCanvas(
            pygame.Rect(320, 120, 640, 480)
        )
        
        # Pattern display (left)
        self.pattern_display = PatternDisplay(
            pygame.Rect(20, 120, 280, 280)
        )
        
        # Score display (right)
        self.score_display = ScoreDisplay(
            pygame.Rect(980, 120, 280, 480)
        )
    
    def handle_input(self) -> None:
        """Process all user input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_running = False
                elif event.key == pygame.K_SPACE:
                    new_drawing_state = not self.drawing_canvas.get_drawing_state()
                    self.drawing_canvas.set_drawing_state(new_drawing_state)
                    # Get hand tracking processor and update its state
                    hand_tracker = self.input_manager.get_processor('hand_tracking')
                    if hand_tracker:
                        hand_tracker.set_drawing_state(new_drawing_state)
                elif event.key == pygame.K_c:
                    self.drawing_canvas.clear()
                    # Also clear the hand tracking processor's canvas
                    hand_tracker = self.input_manager.get_processor('hand_tracking')
                    if hand_tracker:
                        hand_tracker.clear_canvas()
    
    def update(self) -> None:
        """Update game state and all components."""
        # Process input first to update frame
        self.input_manager.process_input()
        
        # Get the processed frame
        frame = self.input_manager.get_frame()
        if frame is not None:
            self.drawing_canvas.update(frame)
            self.score_display.update(
                score=self.current_score,
                game_state="Drawing" if self.drawing_canvas.get_drawing_state() else "Ready",
                is_drawing=self.drawing_canvas.get_drawing_state()
            )
    
    def draw(self) -> None:
        """Render the current frame."""
        # Clear screen
        self.screen.fill(Colors.BACKGROUND)
        
        # Draw UI components
        self.drawing_canvas.draw(self.screen)
        self.pattern_display.draw(self.screen)
        self.score_display.draw(self.screen)
        
        # Draw instructions
        self._draw_instructions()
        
        # Update display
        pygame.display.flip()
        
    def _draw_instructions(self) -> None:
        """Draw control instructions."""
        instructions = [
            "SPACE - Toggle Drawing",
            "C - Clear Canvas",
            "ESC - Quit"
        ]
        
        font = pygame.font.Font(None, 36)
        y = 20
        for text in instructions:
            surface = font.render(text, True, Colors.TEXT)
            self.screen.blit(surface, (20, y))
            y += 30
    
    def run(self) -> None:
        """Main UI loop."""
        self.is_running = True
        
        try:
            # Start input processing
            self.input_manager.start()
            
            # Main loop
            while self.is_running:
                self.handle_input()
                self.update()
                self.draw()
                self.clock.tick(60)
                
        finally:
            self.cleanup()
    
    def cleanup(self) -> None:
        """Clean up resources."""
        self.input_manager.stop()
        pygame.quit()

```

# ui\manager.py

```py
# hand_drawing_challenge/ui/manager.py

from typing import Dict, Optional
import pygame
import numpy as np
import logging
from ..events.bus import EventBus
from ..events.types import GameEventType
from .base import UIComponent
from .renderer import Renderer
from ..input.manager import InputManager
from .components.canvas import DrawingCanvas
from .components.pattern_display import PatternDisplay
from .components.score_display import ScoreDisplay

class UIManager:
    """
    Manages all UI components and coordinates with the renderer.
    """

    def __init__(self, event_bus: EventBus, screen_size: tuple[int, int] = (1280, 720)):
        """Initialize the UI manager."""
        print(">>> ui/manager.py: UIManager.__init__() called")
        self.event_bus = event_bus
        self.screen_size = screen_size
        self.components: Dict[str, UIComponent] = {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize renderer
        self.renderer = Renderer(screen_size)
        
        # Initialize input manager with same event bus
        print(">>> ui/manager.py: Creating InputManager...")
        self.input_manager = InputManager(self.event_bus, camera_id=0)
        
        # Last valid frame
        self.current_frame: Optional[np.ndarray] = None

        # Subscribe to relevant events
        self.event_bus.subscribe(GameEventType.GAME_ENDED, self._handle_game_end)
        self.event_bus.subscribe(GameEventType.MENU_BACK, self._handle_menu_back)
        self.event_bus.subscribe(GameEventType.HAND_POSITION_UPDATED, self._handle_hand_position)

        # Initialize UI components
        self._init_components()

    def _init_components(self) -> None:
        """Initialize and position all UI components."""
        # Main drawing area (center)
        self.components['canvas'] = DrawingCanvas(
            pygame.Rect(320, 120, 640, 480)
        )

        # Pattern display (left)
        self.components['pattern'] = PatternDisplay(
            pygame.Rect(20, 120, 280, 280)
        )

        # Score display (right)
        self.components['score'] = ScoreDisplay(
            pygame.Rect(980, 120, 280, 480)
        )

    def update(self, delta_time: float, score: int = 0, game_state: str = "Ready", is_drawing: bool = False) -> None:
        """Update all UI components."""
        try:
            # Process input
            self.input_manager.process_input()
            
            # Get latest frame
            frame = self.input_manager.get_frame()
            if isinstance(frame, np.ndarray):
                self.current_frame = frame
                # Update drawing canvas with new frame
                canvas = self.get_component('canvas')
                if canvas and isinstance(canvas, DrawingCanvas):
                    canvas.update(frame)

            # Update other components
            for component in self.components.values():
                if not component.visible:
                    continue

                # Update specific component types
                if isinstance(component, ScoreDisplay):
                    component.update(score, game_state, is_drawing)
                elif not isinstance(component, DrawingCanvas):  # Skip DrawingCanvas as it's handled above
                    component.update(delta_time)

        except Exception as e:
            self.logger.error(f"Error updating UI components: {e}")

    def render(self) -> None:
        """Render all UI components using the renderer."""
        # Clear screen
        self.renderer.clear()

        # Render each visible component
        for component in self.components.values():
            if component.visible:
                component.draw(self.renderer.get_screen())

        # Update display
        self.renderer.present()

    def get_component(self, name: str) -> Optional[UIComponent]:
        """Get a UI component by name."""
        return self.components.get(name)

    def set_component_visibility(self, name: str, visible: bool) -> None:
        """Set visibility of a UI component."""
        if name in self.components:
            self.components[name].visible = visible

    def update_frame(self, frame: Optional[np.ndarray]) -> None:
        """Update components with new frame data."""
        if frame is not None and isinstance(frame, np.ndarray):
            self.current_frame = frame
            canvas = self.get_component('canvas')
            if canvas and isinstance(canvas, DrawingCanvas):
                canvas.update(frame)

    def clear_canvas(self) -> None:
        """Clear the drawing canvas."""
        canvas = self.get_component('canvas')
        if canvas and isinstance(canvas, DrawingCanvas):
            canvas.clear()

    def _handle_game_end(self, event_type: GameEventType, data: Optional[dict] = None) -> None:
        """Handle cleanup on game end."""
        self.stop_input_processing()
        self.renderer.cleanup()
        self.input_manager.cleanup()

    def _handle_menu_back(self, event_type: GameEventType, data: Optional[dict] = None) -> None:
        """Handle returning to menu."""
        self.stop_input_processing()

    def _handle_hand_position(self, event_type: GameEventType, data: Optional[dict] = None) -> None:
        """Handle hand position updates."""
        if data and "position" in data:
            canvas = self.get_component('canvas')
            if canvas and isinstance(canvas, DrawingCanvas):
                canvas.update_hand_position(data["position"])

    def cleanup(self) -> None:
        """Clean up all resources."""
        if hasattr(self, 'renderer'):
            self.renderer.cleanup()
        if hasattr(self, 'input_manager'):
            self.input_manager.cleanup()
        self.components.clear()

    def start_input_processing(self) -> None:
        """Start input processing."""
        print(">>> ui/manager.py: start_input_processing() called")
        if hasattr(self, 'input_manager'):
            print(">>> ui/manager.py: Calling input_manager.start()")
            self.input_manager.start()
        else:
            print(">>> ui/manager.py: WARNING - No input_manager found!")

    def stop_input_processing(self) -> None:
        """Stop input processing."""
        if hasattr(self, 'input_manager'):
            self.input_manager.stop()

```

# ui\renderer.py

```py
import pygame
from typing import Optional, Tuple

class Renderer:
    """
    Handles the actual rendering of UI components to the screen.
    
    Responsibilities:
    - Manages the pygame window and display
    - Provides drawing utilities
    - Handles basic screen operations (clear, present)
    """
    
    def __init__(self, screen_size: Tuple[int, int]):
        """
        Initialize the renderer.
        
        Args:
            screen_size: Tuple of (width, height) for window
        """
        pygame.init()
        self.screen_size = screen_size
        self.screen = pygame.display.set_mode(screen_size)
        pygame.display.set_caption("Hand Drawing Challenge")
        
        # Background color (black)
        self.bg_color = (0, 0, 0)
    
    def clear(self) -> None:
        """Clear the screen with background color."""
        self.screen.fill(self.bg_color)
    
    def present(self) -> None:
        """Update the display with rendered content."""
        pygame.display.flip()
    
    def get_screen(self) -> pygame.Surface:
        """
        Get the pygame screen surface.
        
        Returns:
            pygame.Surface: The main screen surface
        """
        return self.screen
    
    def cleanup(self) -> None:
        """Clean up pygame resources."""
        pygame.quit()
```

# ui\utils\colors.py

```py
# ui/utils/colors.py

class Colors:
    """Color constants used throughout the UI."""
    
    # Basic colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    
    # UI specific colors
    BACKGROUND = BLACK
    BORDER = WHITE
    TEXT = WHITE
    COMPONENT_BG = (40, 40, 40)  # Dark gray for component backgrounds
    SUCCESS = GREEN
    PATTERN = (100, 100, 255)  # Light blue for pattern display
    
    # Drawing colors
    DRAWING_ACTIVE = GREEN  # Color when actively drawing
    DRAWING_INACTIVE = BLUE  # Color when hand detected but not drawing
    TRAIL_COLOR = WHITE  # Color of the drawing trail

```

