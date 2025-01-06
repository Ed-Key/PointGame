# __init__.py

```py
# This file makes hand_drawing_challenge a Python package

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
{}
```

# .pytest_cache\v\cache\nodeids

```
[
  "tests/test_competitive_mode.py::TestCompetitiveMode::test_event_emission",
  "tests/test_competitive_mode.py::TestCompetitiveMode::test_multiple_players",
  "tests/test_competitive_mode.py::TestCompetitiveMode::test_player_state_updates",
  "tests/test_competitive_mode.py::TestCompetitiveMode::test_turn_management"
]
```

# .pytest_cache\v\cache\stepwise

```
[]
```

# game\__init__.py

```py
from typing import Optional, Tuple, Dict, Type
from .base import GameMode, GameConfig
from .modes.single_player import SinglePlayerMode
from .modes.competitive import CompetitiveMode

# Map mode types to their implementations
MODE_TYPES: Dict[str, Type[GameMode]] = {
    "single_player": SinglePlayerMode,
    "competitive": CompetitiveMode
}

def create_game_mode(mode_type: str, screen_size: Tuple[int, int], config: Optional[GameConfig] = None) -> Optional[GameMode]:
    """Factory function to create game modes.
    
    Args:
        mode_type: Type of game mode to create ("single_player" or "competitive")
        screen_size: Screen dimensions (width, height)
        config: Optional game configuration
    
    Returns:
        Created game mode instance or None if type is invalid
    """
    print(f"Creating game mode: {mode_type}")  # Debug print
    mode_class = MODE_TYPES.get(mode_type)
    if mode_class:
        print(f"Found mode class: {mode_class.__name__}")  # Debug print
        mode = mode_class(screen_size, config)
        print("Mode instance created, initializing...")  # Debug print
        mode.initialize()  # Make sure we call initialize
        print("Mode initialized successfully")  # Debug print
        return mode
    print(f"No mode class found for type: {mode_type}")  # Debug print
    return None

# Export commonly used types and functions
__all__ = [
    'GameMode',
    'GameConfig',
    'create_game_mode'
]
```

# game\base.py

```py
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum, auto

class GameStateType(Enum):
    """Enum defining different game states."""
    MENU = auto()
    PLAYING = auto()
    RESULTS = auto()
    PAUSED = auto()

@dataclass
class GameConfig:
    """Configuration for game settings.
    
    Attributes:
        difficulty (int): Current difficulty level
        max_time (int): Maximum time per round in seconds
        pattern_complexity (int): Complexity level for patterns
        required_accuracy (float): Minimum accuracy required to pass
    """
    difficulty: int = 1
    max_time: int = 60
    pattern_complexity: int = 1
    required_accuracy: float = 0.7

class GameState(ABC):
    """Abstract base class for game states."""
    
    def __init__(self):
        """Initialize the game state."""
        self.next_state: Optional[GameStateType] = None
    
    def on_enter(self) -> None:
        """Called when entering this state. Override to provide initialization logic."""
        pass
    
    def on_exit(self) -> None:
        """Called when exiting this state. Override to provide cleanup logic."""
        pass
    
    @abstractmethod
    def update(self, delta_time: float) -> None:
        """Update the state.
        
        Args:
            delta_time: Time elapsed since last update in seconds
        """
        pass
    
    @abstractmethod
    def draw(self) -> None:
        """Draw the current state."""
        pass
    
    @abstractmethod
    def handle_input(self, event: Any) -> None:
        """Handle input events.
        
        Args:
            event: Input event to process
        """
        pass
    
    def transition_to(self, state: GameStateType) -> None:
        """Request transition to a new state.
        
        Args:
            state: State to transition to
        """
        self.next_state = state

class GameMode(ABC):
    """Abstract base class for game modes."""
    
    def __init__(self, config: GameConfig):
        """Initialize the game mode.
        
        Args:
            config: Game configuration settings
        """
        self.config = config
        self.states: Dict[GameStateType, GameState] = {}
        self.current_state: Optional[GameState] = None
        self.score = 0
        self.is_active = False
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize the game mode and its states."""
        pass
    
    def update(self, delta_time: float) -> None:
        """Update the current game state.
        
        Args:
            delta_time: Time elapsed since last update in seconds
        """
        if self.current_state:
            self.current_state.update(delta_time)
            
            # Check for state transition
            if self.current_state.next_state:
                self.transition_to(self.current_state.next_state)
    
    def draw(self) -> None:
        """Draw the current game state."""
        if self.current_state:
            self.current_state.draw()
    
    def handle_input(self, event: Any) -> None:
        """Handle input events.
        
        Args:
            event: Input event to process
        """
        if self.current_state:
            self.current_state.handle_input(event)
    
    def transition_to(self, state_type: GameStateType) -> None:
        """Transition to a new game state.
        
        Args:
            state_type: Type of state to transition to
        """
        if state_type in self.states:
            # Call exit on current state if it exists
            if self.current_state:
                self.current_state.on_exit()
            
            # Set new state
            self.current_state = self.states[state_type]
            self.current_state.next_state = None
            
            # Call enter on new state
            self.current_state.on_enter()
    
    def start(self) -> None:
        """Start the game mode."""
        print("GameMode.start() called")  # Debug print
        self.is_active = True
        self.score = 0
        if self.current_state:
            print("Calling on_enter for current state")  
            self.current_state.on_enter()
    
    def stop(self) -> None:
        """Stop the game mode."""
        if self.current_state:
            self.current_state.on_exit()
        self.is_active = False
        self.current_state = None

class SinglePlayerMode(GameMode):
    """Implementation of single player game mode."""
    
    def initialize(self) -> None:
        """Initialize single player mode states."""
        # Implement single player specific initialization
        pass

class CompetitiveMode(GameMode):
    """Implementation of competitive game mode."""
    
    def initialize(self) -> None:
        """Initialize competitive mode states."""
        # Implement competitive specific initialization
        pass
```

# game\managers\__init__.py

```py
from .competitive_manager import CompetitiveGameManager
from .event_manager import EventManager
from .player_manager import PlayerDisplayManager

__all__ = ['CompetitiveGameManager', 'EventManager', 'PlayerDisplayManager']

```

# game\managers\competitive_manager.py

```py
# game/managers/competitive_manager.py
import uuid
from dataclasses import dataclass
from typing import Dict, List, Optional
from .event_manager import EventManager, GameEvent

@dataclass
class PlayerState:
    """Enhanced player state tracking."""
    id: str  # Unique player identifier
    name: str
    score: int = 0
    completed: bool = False
    accuracy: float = 0.0
    turn_order: int = 0

class CompetitiveGameManager:
    """Centralized game state management for competitive mode."""
    def __init__(self):
        self.players: Dict[str, PlayerState] = {}
        self.current_turn_idx: int = -1  # Start at -1 so first next_turn() goes to 0
        self._turn_order: List[str] = []
        self.event_manager = EventManager()

    def add_player(self, name: str) -> str:
        """Add a new player to the game.
        
        Args:
            name: Player's display name
            
        Returns:
            str: Unique player ID
        """
        player_id = str(uuid.uuid4())
        self.players[player_id] = PlayerState(
            id=player_id,
            name=name,
            turn_order=len(self.players)
        )
        self._turn_order.append(player_id)
        return player_id
        
    def next_turn(self) -> Optional[str]:
        """Advance to the next player's turn.
        
        Returns:
            Optional[str]: ID of the next player or None if game is over
        """
        if not self._turn_order:
            return None
        
        self.current_turn_idx = (self.current_turn_idx + 1) % len(self._turn_order)
        next_player_id = self._turn_order[self.current_turn_idx]
        
        self.event_manager.emit(
            GameEvent.TURN_CHANGED,
            next_player_id,
            self.players[next_player_id].name
        )
        
        return next_player_id
    
    def get_current_player(self) -> Optional[str]:
        """Get the current player's ID.
        
        Returns:
            Optional[str]: Current player's ID or None if no game in progress
        """
        if not self._turn_order or self.current_turn_idx < 0:
            return None
        return self._turn_order[self.current_turn_idx]

    def update_player_score(self, player_id: str, score: int) -> None:
        """Update a player's score.
        
        Args:
            player_id: Player's unique ID
            score: New score value
        """
        if player_id in self.players:
            self.players[player_id].score = score
            self.event_manager.emit(
                GameEvent.PLAYER_SCORED,
                player_id,
                score
            )
    
    def get_player_count(self) -> int:
        """Get the number of players in the game.
        
        Returns:
            int: Number of players
        """
        return len(self.players)

    def get_player_turn_order(self) -> List[str]:
        """Get the list of player IDs in turn order.
        
        Returns:
            List[str]: Player IDs in turn order
        """
        return self._turn_order.copy()

    def mark_player_completed(self, player_id: str, accuracy: float = 0.0) -> None:
        """Mark a player's turn as completed.
        
        Args:
            player_id: Player's unique ID
            accuracy: Player's drawing accuracy
        """
        if player_id in self.players:
            self.players[player_id].completed = True
            self.players[player_id].accuracy = accuracy
```

# game\managers\event_manager.py

```py
# game/managers/event_manager.py
from enum import Enum
from collections import defaultdict
from typing import Callable, Dict, List

class GameEvent(Enum):
    """Game event types."""
    TURN_CHANGED = "turn_changed"
    PLAYER_SCORED = "player_scored"
    GAME_ENDED = "game_ended"

class EventManager:
    """Manages game event subscriptions and notifications."""
    
    def __init__(self):
        self._handlers: Dict[GameEvent, List[Callable]] = defaultdict(list)
    
    def subscribe(self, event: GameEvent, handler: Callable) -> None:
        """Subscribe to a game event.
        
        Args:
            event: Event type to subscribe to
            handler: Callback function to handle the event
        """
        self._handlers[event].append(handler)
    
    def unsubscribe(self, event: GameEvent, handler: Callable) -> None:
        """Remove a subscription from an event.
        
        Args:
            event: Event type to unsubscribe from
            handler: Handler to remove
        """
        if event in self._handlers:
            self._handlers[event].remove(handler)
    
    def emit(self, event: GameEvent, *args, **kwargs) -> None:
        """Emit an event to all subscribers.
        
        Args:
            event: Event type to emit
            *args: Positional arguments for event handlers
            **kwargs: Keyword arguments for event handlers
        """
        for handler in self._handlers[event]:
            handler(*args, **kwargs)
```

# game\managers\player_manager.py

```py
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
```

# game\modes\__init__.py

```py
"""Game mode implementations for Hand Drawing Challenge."""

from .single_player import SinglePlayerMode
from .competitive import CompetitiveMode, CompetitivePlayingState

__all__ = [
    'SinglePlayerMode',
    'CompetitiveMode',
    'CompetitivePlayingState'
]

```

# game\modes\competitive.py

```py
# game/modes/competitive.py
from typing import Dict, Tuple, Optional, Any
import pygame
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
        
        # Draw player information
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
        self.canvas.fill((0, 0, 0))
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
```

# game\modes\single_player.py

```py
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
```

# game\states\__init__.py

```py
from .menu_state import MenuState
from .playing_state import PlayingState
from .results_state import ResultsState

__all__ = [
    'MenuState',
    'PlayingState',
    'ResultsState'
]
```

# game\states\menu_state.py

```py
import pygame
from typing import Any, List, Tuple, Optional, Callable
from ..base import GameState, GameStateType, GameMode
from ui.utils.colors import Colors

class MenuItem:
    """Represents a clickable menu item."""
    
    def __init__(self, text: str, position: Tuple[int, int], action: Callable[[], None]):
        """Initialize menu item.
        
        Args:
            text: Text to display
            position: (x, y) position to render
            action: Game state to transition to when clicked
        """
        self.text = text
        self.position = position
        self.action = action
        self.font = pygame.font.Font(None, 48)
        self.is_hovered = False
        
        # Create text surfaces for normal and hover states
        self.text_normal = self.font.render(text, True, Colors.TEXT)
        self.text_hover = self.font.render(text, True, Colors.TEXT)
        
        # Create rect for collision detection
        self.rect = self.text_normal.get_rect(center=position)
    
    def update(self, mouse_pos: Tuple[int, int]) -> None:
        """Update hover state based on mouse position.
        
        Args:
            mouse_pos: Current mouse position
        """
        self.is_hovered = self.rect.collidepoint(mouse_pos)
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the menu item.
        
        Args:
            screen: Surface to draw on
        """
        text_surface = self.text_hover if self.is_hovered else self.text_normal
        screen.blit(text_surface, self.rect)

class MenuState(GameState):
    """Game menu state handling."""
    
    def __init__(self, screen_size: Tuple[int, int], mode_factory=None):
        """Initialize menu state.
        
        Args:
            screen_size: (width, height) of game window
            mode_factory: Callback to create game modes
        """
        super().__init__()
        self.screen_size = screen_size
        self.background_color = Colors.BACKGROUND
        self.items: List[MenuItem] = []
        self.current_mode: Optional[GameMode] = None
        self.mode_factory = mode_factory

        self.setup_menu_items()
        
        # Title setup
        self.title_font = pygame.font.Font(None, 64)
        self.title = self.title_font.render("Hand Drawing Challenge", True, Colors.TEXT)
        self.title_rect = self.title.get_rect(
            centerx=screen_size[0] // 2,
            top=50
        )
    
    def setup_menu_items(self) -> None:
        """Create and position menu items."""
        # Calculate positions based on screen size
        center_x = self.screen_size[0] // 2
        start_y = self.screen_size[1] // 2
        spacing = 80

        items_data = [
            ("Single Player", lambda: self.start_game_mode("single_player")),
            ("Competitive", lambda: self.start_game_mode("competitive")),
            ("Exit", lambda: (pygame.quit(), exit(0)))
        ]
        
        for i, (text, callback) in enumerate(items_data):
            y_pos = start_y + i * spacing
            self.items.append(MenuItem(text, (center_x, y_pos), callback))
    
    def start_game_mode(self, mode_type: str) -> None:
        """Start a specific game mode.
        
        Args:
            mode_type: Type of game mode to start ("single_player" or "competitive")
        """
        if self.mode_factory:
            self.current_mode = self.mode_factory(mode_type, self.screen_size)
            if self.current_mode:
                self.current_mode.initialize()
                self.current_mode.start_new_game()
                self.transition_to(GameStateType.PLAYING)
    
    def update(self, delta_time: float) -> None:
        """Update menu state.
        
        Args:
            delta_time: Time elapsed since last update
        """
        mouse_pos = pygame.mouse.get_pos()
        for item in self.items:
            item.update(mouse_pos)
    
    def draw(self) -> None:
        """Draw the menu state."""
        # Get the game screen
        screen = pygame.display.get_surface()
        
        # Draw background
        screen.fill(self.background_color)
        
        # Draw title
        screen.blit(self.title, self.title_rect)
        
        # Draw menu items
        for item in self.items:
            item.draw(screen)
    
    def handle_input(self, event: Any) -> None:
        """Handle input events.
        
        Args:
            event: Pygame event to process
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Left click
            for item in self.items:
                if item.is_hovered:
                    item.action()  # Call the callback function

```

# game\states\playing_state.py

```py
import pygame
import cv2
import numpy as np
from typing import Any, Tuple, Optional
from ..base import GameState, GameStateType
from ui.components.canvas import DrawingCanvas
from ui.components.pattern_display import PatternDisplay
from ui.components.score_display import ScoreDisplay
from ui.utils.colors import Colors
from input_processing.camera import Camera, CameraConfig, CameraError
from input_processing.hand_tracking import HandTracker, HandPoint
from input_processing.drawing_tracker import DrawingTracker

class PlayingState(GameState):
    """Game playing state handling."""
    
    def __init__(self, screen_size: Tuple[int, int]):
        """Initialize playing state."""
        super().__init__()
        print("Initializing PlayingState...") # Debug print
        
        self.screen_size = screen_size
        
        # Initialize components and input processing
        self.setup_ui_components()
        
        # Game state
        self.time_remaining = 60.0  # 60 seconds per round
        self.current_score = 0
        self.is_paused = False
        
        # Drawing state
        self.canvas = np.zeros((480, 640, 3), dtype=np.uint8)
        self.is_drawing = False
        
        # Font setup
        self.font = pygame.font.Font(None, 36)
        
        # Initialize trackers first
        print("Initializing trackers...") # Debug print
        self.tracker = HandTracker()
        self.drawing_tracker = DrawingTracker(width=640, height=480)
        
        # Initialize camera last
        print("Setting up camera...") # Debug print
        camera_config = CameraConfig(
            width=640,
            height=480,
            fps=30,
            mirror=False,
            device_id=0  # Explicitly set to use first camera
        )
        self.camera = Camera(camera_config)
        print("Camera object created") # Debug print
        
    def setup_ui_components(self) -> None:
        """Initialize UI components."""
        # Calculate component positions based on screen size
        canvas_size = (640, 480)
        pattern_size = (280, 280)
        score_size = (280, 480)
        
        # Center canvas horizontally
        canvas_x = (self.screen_size[0] - canvas_size[0]) // 2
        canvas_y = 120
        
        # Pattern display on left
        pattern_x = 20
        pattern_y = canvas_y
        
        # Score display on right
        score_x = self.screen_size[0] - score_size[0] - 20
        score_y = canvas_y
        
        # Create components
        self.canvas_rect = pygame.Rect(canvas_x, canvas_y, *canvas_size)
        self.pattern_display = PatternDisplay(
            pygame.Rect(pattern_x, pattern_y, *pattern_size)
        )
        self.score_display = ScoreDisplay(
            pygame.Rect(score_x, score_y, *score_size)
        )
    
    def on_enter(self) -> None:
        """Called when entering this state."""
        print("Entering playing state...") # Debug print
        try:
            if hasattr(self, 'camera'):
                print("Starting camera...") # Debug print
                self.camera.start()
                print("Camera started successfully") # Debug print
            else:
                print("No camera attribute found in on_enter") # Debug print
            
            # Reset game state
            self.time_remaining = 60.0
            self.current_score = 0
            self.is_paused = False
            self.is_drawing = False
            self.canvas = np.zeros((480, 640, 3), dtype=np.uint8)
            self.drawing_tracker.clear()
            
        except Exception as e:
            print(f"Error in on_enter: {e}")
            self.transition_to(GameStateType.MENU)
    
    def on_exit(self) -> None:
        """Called when exiting this state."""
        print("Exiting playing state...") # Debug print
        self.cleanup()
    
    def update_camera_feed(self) -> Optional[pygame.Surface]:
        """Update and display the camera feed."""
        try:
            if not hasattr(self, 'camera'):
                print("No camera attribute found") # Debug print
                return None
                
            if not self.camera._is_running:
                print("Camera exists but is not running") # Debug print
                return None
                
            success, frame = self.camera.get_frame()
            if not success:
                print("Failed to get camera frame") # Debug print
                return None
            
            # Process hand tracking
            hand_point = self.tracker.get_index_finger_tip(frame)
            
            # Update drawing tracker and get smoothed position
            smoothed_pos = self.drawing_tracker.update(hand_point, self.is_drawing)
            
            if smoothed_pos:
                x, y = smoothed_pos
                # Draw current position
                color = (0, 255, 0) if self.is_drawing else (0, 0, 255)
                cv2.circle(frame, (x, y), 5, color, -1)
                
                # Draw trail
                trail_points = self.drawing_tracker.get_trail_points()
                if len(trail_points) > 1:
                    cv2.line(self.canvas,
                           trail_points[-2],
                           trail_points[-1],
                           (0, 255, 0),
                           2)
            
            # Combine frame and canvas
            display = cv2.addWeighted(frame, 1.0, self.canvas, 0.7, 0)
            
            # Convert to pygame surface
            display = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
            display = pygame.surfarray.make_surface(display)
            display = pygame.transform.rotate(display, 270)
            
            return display
            
        except Exception as e:
            print(f"Error in update_camera_feed: {str(e)}") # Debug print
            return None
    
    def update(self, delta_time: float) -> None:
        """Update playing state."""
        if self.is_paused:
            return
            
        # Update time
        self.time_remaining -= delta_time
        if self.time_remaining <= 0:
            self.cleanup()
            self.transition_to(GameStateType.RESULTS)
            return
        
        # Update score display
        self.score_display.update(
            score=self.current_score,
            game_state="Playing",
            is_drawing=self.is_drawing
        )
    
    def draw(self) -> None:
        """Draw the playing state."""
        screen = pygame.display.get_surface()
        screen.fill(Colors.BACKGROUND)
        
        # Update and draw camera feed
        display = self.update_camera_feed()
        if display:
            screen.blit(display, self.canvas_rect)
        else:
            # Draw placeholder if camera feed isn't available
            pygame.draw.rect(screen, Colors.BUTTON_NORMAL, self.canvas_rect)
            no_camera_text = self.font.render("Camera not available", True, Colors.TEXT)
            text_rect = no_camera_text.get_rect(center=self.canvas_rect.center)
            screen.blit(no_camera_text, text_rect)
        
        # Draw UI components
        pygame.draw.rect(screen, Colors.BORDER, self.canvas_rect, 2)
        self.pattern_display.draw(screen)
        self.score_display.draw(screen)
        
        # Draw time remaining
        time_text = f"Time: {int(self.time_remaining)}s"
        time_surface = self.font.render(time_text, True, Colors.TEXT)
        screen.blit(time_surface, (20, 20))
        
        # Draw pause overlay if paused
        if self.is_paused:
            self._draw_pause_overlay(screen)
    
    def _draw_pause_overlay(self, screen: pygame.Surface) -> None:
        """Draw pause menu overlay."""
        overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        
        pause_text = self.font.render("PAUSED", True, Colors.TEXT)
        text_rect = pause_text.get_rect(center=(self.screen_size[0] // 2, 
                                              self.screen_size[1] // 2))
        
        screen.blit(overlay, (0, 0))
        screen.blit(pause_text, text_rect)
    
    def handle_input(self, event: Any) -> None:
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.is_paused = not self.is_paused
            elif event.key == pygame.K_SPACE:
                self.is_drawing = not self.is_drawing
            elif event.key == pygame.K_c:
                self.canvas = np.zeros((480, 640, 3), dtype=np.uint8)
                self.drawing_tracker.clear()
            elif event.key == pygame.K_q and self.is_paused:
                self.cleanup()
                self.transition_to(GameStateType.MENU)
    
    def cleanup(self) -> None:
        """Clean up resources."""
        try:
            if hasattr(self, 'camera') and self.camera:
                print("Stopping camera...") # Debug print
                self.camera.stop()
                print("Camera stopped successfully") # Debug print
        except Exception as e:
            print(f"Error stopping camera: {e}")
```

# game\states\results_state.py

```py
import pygame
from typing import Any, Tuple, Dict, Optional
from ..base import GameState, GameStateType
from ui.utils.colors import Colors

class ResultsState(GameState):
    """Game results state handling."""
    
    def __init__(self, screen_size: Tuple[int, int]):
        """Initialize results state.
        
        Args:
            screen_size: (width, height) of game window
        """
        super().__init__()
        self.screen_size = screen_size
        
        # Font setup
        self.title_font = pygame.font.Font(None, 64)
        self.font = pygame.font.Font(None, 36)
        
        # Button setup
        button_width = 200
        button_height = 50
        self.button_rects: Dict[str, pygame.Rect] = {
            'menu': pygame.Rect(
                (self.screen_size[0] - button_width) // 2,
                self.screen_size[1] - 150,
                button_width,
                button_height
            ),
            'retry': pygame.Rect(
                (self.screen_size[0] - button_width) // 2,
                self.screen_size[1] - 220,
                button_width,
                button_height
            )
        }
        
        self.hovered_button: Optional[str] = None
        self.final_score = 0
        self.accuracy = 0.0
        self.time_bonus = 0
        
        # Achievement tracking
        self.new_achievements: list[str] = []
        self.show_achievements = False
        self.achievement_timer = 0
    
    def set_results(self, score: int, accuracy: float, time_bonus: int, 
                   new_achievements: Optional[list[str]] = None) -> None:
        """Set the final results to display.
        
        Args:
            score: Final score
            accuracy: Drawing accuracy percentage
            time_bonus: Time bonus points
            new_achievements: List of newly unlocked achievements
        """
        self.final_score = score
        self.accuracy = accuracy
        self.time_bonus = time_bonus
        self.new_achievements = new_achievements or []
        self.show_achievements = bool(self.new_achievements)
        self.achievement_timer = 3.0  # Show achievements for 3 seconds
    
    def update(self, delta_time: float) -> None:
        """Update results state.
        
        Args:
            delta_time: Time elapsed since last update
        """
        mouse_pos = pygame.mouse.get_pos()
        
        # Update button hover states
        self.hovered_button = None
        for button_name, button_rect in self.button_rects.items():
            if button_rect.collidepoint(mouse_pos):
                self.hovered_button = button_name
                break
        
        # Update achievement display timer
        if self.show_achievements:
            self.achievement_timer -= delta_time
            if self.achievement_timer <= 0:
                self.show_achievements = False
    
    def draw(self) -> None:
        """Draw the results state."""
        screen = pygame.display.get_surface()
        screen.fill(Colors.BACKGROUND)
        
        # Draw title
        title = self.title_font.render("Results", True, Colors.TEXT)
        title_rect = title.get_rect(
            centerx=self.screen_size[0] // 2,
            top=50
        )
        screen.blit(title, title_rect)
        
        # Draw results
        results_text = [
            f"Final Score: {self.final_score}",
            f"Accuracy: {self.accuracy:.1f}%",
            f"Time Bonus: +{self.time_bonus}"
        ]
        
        y_offset = 200
        for text in results_text:
            surface = self.font.render(text, True, Colors.TEXT)
            rect = surface.get_rect(
                centerx=self.screen_size[0] // 2,
                top=y_offset
            )
            screen.blit(surface, rect)
            y_offset += 50
        
        # Draw achievement notifications if active
        if self.show_achievements:
            self._draw_achievements(screen)
        
        # Draw buttons
        self._draw_buttons(screen)
    
    def _draw_buttons(self, screen: pygame.Surface) -> None:
        """Draw menu buttons.
        
        Args:
            screen: Surface to draw on
        """
        button_text = {
            'menu': 'Main Menu',
            'retry': 'Try Again'
        }
        
        for button_name, rect in self.button_rects.items():
            # Draw button background
            color = Colors.BUTTON_HOVER if button_name == self.hovered_button else Colors.BUTTON_NORMAL
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, Colors.BORDER, rect, 2)
            
            # Draw button text
            text = self.font.render(button_text[button_name], True, Colors.TEXT)
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)
    
    def _draw_achievements(self, screen: pygame.Surface) -> None:
        """Draw achievement notifications.
        
        Args:
            screen: Surface to draw on
        """
        if not self.new_achievements:
            return
            
        # Create semi-transparent overlay
        overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        
        # Draw achievement box
        box_width = 400
        box_height = 100 + (len(self.new_achievements) * 40)
        box_rect = pygame.Rect(
            (self.screen_size[0] - box_width) // 2,
            (self.screen_size[1] - box_height) // 2,
            box_width,
            box_height
        )
        
        pygame.draw.rect(overlay, (50, 50, 50, 230), box_rect)
        pygame.draw.rect(overlay, Colors.BORDER, box_rect, 2)
        
        # Draw achievement title
        title = self.font.render("New Achievements!", True, Colors.TEXT)
        title_rect = title.get_rect(
            centerx=box_rect.centerx,
            top=box_rect.top + 20
        )
        
        # Draw achievements list
        y_offset = title_rect.bottom + 20
        for achievement in self.new_achievements:
            text = self.font.render(f"🏆 {achievement}", True, Colors.TEXT)
            rect = text.get_rect(
                centerx=box_rect.centerx,
                top=y_offset
            )
            overlay.blit(text, rect)
            y_offset += 40
        
        # Draw overlay
        screen.blit(overlay, (0, 0))
    
    def handle_input(self, event: Any) -> None:
        """Handle input events.
        
        Args:
            event: Pygame event to process
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Left click
            if self.hovered_button == 'menu':
                self.transition_to(GameStateType.MENU)
            elif self.hovered_button == 'retry':
                self.transition_to(GameStateType.PLAYING)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Skip achievement display
                self.show_achievements = False
                self.achievement_timer = 0
            elif event.key == pygame.K_ESCAPE:
                self.transition_to(GameStateType.MENU)
```

# input_processing\__init__.py

```py
# Initialize the input_processing package

# Import specific classes/functions to make them available directly
from .camera import Camera, CameraConfig, CameraError
from .hand_tracking import HandTracker

# Optionally define an __all__ list to control what gets imported with `from input_processing import *`
__all__ = [
    "Camera",
    "CameraConfig",
    "CameraError",
    "HandTracker"
]

```

# input_processing\camera.py

```py
# input_processing/camera.py
import cv2
import numpy as np
from dataclasses import dataclass
from typing import Tuple, Optional

@dataclass
class CameraConfig:
    """Configuration for camera setup.
    
    Attributes:
        width (int): Frame width in pixels
        height (int): Frame height in pixels
        fps (int): Target frames per second
        device_id (int): Camera device identifier
        mirror (bool): Whether to mirror the camera feed horizontally
    """
    width: int = 640
    height: int = 480
    fps: int = 60
    device_id: int = 0
    mirror: bool = True

class CameraError(Exception):
    """Custom exception for camera-related errors."""
    pass

class Camera:
    """Manages camera operations for input capture."""
    
    def __init__(self, config: CameraConfig = CameraConfig()):
        """Initialize camera with given configuration."""
        print("[Camera] Creating new Camera instance") # Debug print
        self.config = config
        self._capture = None
        self._is_running = False
    
    def start(self) -> None:
        """Start the camera capture."""
        print("[Camera] Attempting to start camera...") # Debug print
        try:
            if self._is_running:
                print("[Camera] Camera is already running") # Debug print
                return
            
            print(f"[Camera] Opening camera device {self.config.device_id}") # Debug print
            self._capture = cv2.VideoCapture(self.config.device_id)
            
            if not self._capture.isOpened():
                print("[Camera] Failed to open camera device") # Debug print
                raise CameraError(f"Failed to open camera device {self.config.device_id}")
            
            print("[Camera] Setting camera properties...") # Debug print
            self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.width)
            self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.height)
            self._capture.set(cv2.CAP_PROP_FPS, self.config.fps)
            
            # Verify camera is working
            print("[Camera] Testing frame capture...") # Debug print
            success, _ = self._capture.read()
            if not success:
                print("[Camera] Failed to capture test frame") # Debug print
                raise CameraError("Failed to capture initial frame")
            
            print("[Camera] Camera initialized successfully") # Debug print
            self._is_running = True
            
        except Exception as e:
            print(f"[Camera] Start failed with error: {str(e)}") # Debug print
            self._is_running = False
            if self._capture is not None:
                self._capture.release()
                self._capture = None
            raise CameraError(f"Camera initialization failed: {str(e)}")
    
    def get_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Capture a single frame from the camera.
        
        Returns:
            Tuple[bool, Optional[np.ndarray]]: Success flag and frame (if successful)
        """
        if not self._is_running:
            raise CameraError("Camera is not started")
        
        try:
            success, frame = self._capture.read()
            if not success:
                print("[Camera] Failed to capture frame") # Debug print
                return False, None
                
            # Mirror the frame if configured
            if self.config.mirror:
                frame = cv2.flip(frame, 1)
                
            return True, frame
        except Exception as e:
            print(f"[Camera] Frame capture failed: {str(e)}") # Debug print
            raise CameraError(f"Frame capture failed: {str(e)}")
    
    def stop(self) -> None:
        """Stop the camera and release resources."""
        print("[Camera] Stopping camera...") # Debug print
        if self._capture is not None:
            self._capture.release()
            self._is_running = False
            print("[Camera] Camera stopped successfully") # Debug print
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
```

# input_processing\drawing_tracker.py

```py
from collections import deque
import numpy as np
from typing import Optional, Tuple, List
from .hand_tracking import HandPoint

class DrawingTracker:
    """Handles drawing input processing with smoothing and stability improvements."""
    
    def __init__(self, 
                 width: int = 640, 
                 height: int = 480,
                 smoothing_window: int = 5,
                 max_jump_distance: int = 100,
                 min_movement_threshold: int = 5):
        """Initialize the drawing tracker.
        
        Args:
            width: Canvas width in pixels
            height: Canvas height in pixels
            smoothing_window: Number of frames to use for position smoothing
            max_jump_distance: Maximum allowed position change between frames
            min_movement_threshold: Minimum movement to register a new point
        """
        self.width = width
        self.height = height
        self.trail_points: List[Tuple[int, int]] = []
        
        # Position smoothing
        self.smoothing_window = smoothing_window
        self.position_history = deque(maxlen=smoothing_window)
        self.last_valid_position: Optional[Tuple[int, int]] = None
        
        # Stability settings
        self.max_jump_distance = max_jump_distance
        self.min_movement_threshold = min_movement_threshold
    
    def _smooth_position(self, new_point: Optional[HandPoint]) -> Optional[Tuple[int, int]]:
        """Smooth the hand position using a moving average and validate movement.
        
        Args:
            new_point: New hand position from tracker
            
        Returns:
            Smoothed and validated (x, y) position or None if invalid
        """
        if new_point is None:
            return self.last_valid_position
            
        # Convert normalized coordinates to pixel coordinates
        x = int(new_point.x * self.width)
        y = int(new_point.y * self.height)
        
        # Validate position is within bounds
        if not (0 <= x < self.width and 0 <= y < self.height):
            return self.last_valid_position
            
        # Check for unrealistic jumps if we have a previous position
        if self.last_valid_position:
            last_x, last_y = self.last_valid_position
            distance = np.sqrt((x - last_x)**2 + (y - last_y)**2)
            if distance > self.max_jump_distance:
                return self.last_valid_position
        
        # Add to position history
        self.position_history.append((x, y))
        
        # Calculate smoothed position
        if len(self.position_history) >= 3:  # Need at least 3 points for stable smoothing
            x_smooth = int(np.mean([p[0] for p in self.position_history]))
            y_smooth = int(np.mean([p[1] for p in self.position_history]))
            
            # Update last valid position
            self.last_valid_position = (x_smooth, y_smooth)
            return x_smooth, y_smooth
            
        return x, y
    
    def _should_add_point(self, new_position: Tuple[int, int]) -> bool:
        """Determine if a new point should be added to the trail.
        
        Args:
            new_position: New smoothed position
            
        Returns:
            True if point should be added, False otherwise
        """
        if not self.trail_points:
            return True
            
        last_x, last_y = self.trail_points[-1]
        new_x, new_y = new_position
        distance = np.sqrt((new_x - last_x)**2 + (new_y - last_y)**2)
        
        return distance >= self.min_movement_threshold

    def update(self, hand_point: Optional[HandPoint], is_drawing: bool) -> Optional[Tuple[int, int]]:
        """Update the drawing tracker with new hand position.
        
        Args:
            hand_point: New hand position from tracker
            is_drawing: Whether currently in drawing mode
            
        Returns:
            Current smoothed position or None if invalid
        """
        smoothed_position = self._smooth_position(hand_point)
        
        if smoothed_position and is_drawing:
            if self._should_add_point(smoothed_position):
                self.trail_points.append(smoothed_position)
        
        return smoothed_position
    
    def clear(self):
        """Clear the drawing trail and reset state."""
        self.trail_points = []
        self.position_history.clear()
        self.last_valid_position = None

    def get_trail_points(self) -> List[Tuple[int, int]]:
        """Get the current trail points.
        
        Returns:
            List of (x, y) coordinates making up the trail
        """
        return self.trail_points
```

# input_processing\hand_tracking.py

```py
# input_processing/hand_tracking.py
import mediapipe as mp
import numpy as np
import cv2
from dataclasses import dataclass
from typing import Optional, Tuple, Any

@dataclass
class HandPoint:
    """Represents a specific point on the hand (like index fingertip).
    
    Attributes:
        x (float): x-coordinate (0-1)
        y (float): y-coordinate (0-1)
        z (float): z-coordinate (depth)
    """
    x: float
    y: float
    z: float

class HandTracker:
    """Tracks hand landmarks using MediaPipe, focused on index finger tracking."""
    
    def __init__(
        self,
        min_detection_confidence: float = 0.7,
        min_tracking_confidence: float = 0.5,
        hands_module: Any = None
    ):
        """Initialize the hand tracker.
        
        Args:
            min_detection_confidence: Minimum confidence for hand detection
            min_tracking_confidence: Minimum confidence for landmark tracking
            hands_module: MediaPipe hands module (for testing)
        """
        hands = hands_module if hands_module is not None else mp.solutions.hands
        self._mp_hands = hands.Hands(
            static_image_mode=False,
            max_num_hands=1,  # Only track one hand for drawing
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
    
    def get_index_finger_tip(self, frame) -> Optional[HandPoint]:
        """Get the position of the index finger tip.
        
        Args:
            frame: Video frame from camera
            
        Returns:
            HandPoint if index finger is detected, None otherwise
        """
        # Convert the BGR image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = self._mp_hands.process(rgb_frame)
            
        # Check if any hands were detected
        if not results.multi_hand_landmarks:
            return None
            
        # Get the first hand detected
        hand_landmarks = results.multi_hand_landmarks[0]
        
        # Index fingertip is landmark 8 in MediaPipe Hands
        index_tip = hand_landmarks.landmark[8]
        
        return HandPoint(
            x=index_tip.x,
            y=index_tip.y,
            z=index_tip.z
        )
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._mp_hands.close()

```

# main.py

```py
# main.py
from ui.game_ui import GameUI

def main():
    """Main entry point for the Hand Drawing Challenge application."""
    try:
        # Create and run game UI
        game = GameUI()
        game.run()
    except Exception as e:
        print(f"Error running application: {e}")
        
if __name__ == "__main__":
    main()
```

# requirements.txt

```txt
opencv-python==4.10.0.84
mediapipe==0.10.20
numpy>=1.24.3
pygame>=2.5.0
pytest>=7.4.0

```

# test_game.py

```py
import pygame
from game.base import GameMode, GameConfig, GameStateType
from game import create_game_mode
from game.states.menu_state import MenuState
from game.states.playing_state import PlayingState
from game.states.results_state import ResultsState

class TestGame(GameMode):
    """Test implementation of GameMode to verify state transitions."""
    
    def __init__(self, screen_size=(1280, 720)):
        """Initialize test game.
        
        Args:
            screen_size: Window size in pixels
        """
        config = GameConfig()  # Use default config for testing
        super().__init__(config)
        self.screen_size = screen_size
        
    def initialize(self) -> None:
        """Initialize game states."""
        # Create all game states
        # Create states with mode factory
        menu_state = MenuState(self.screen_size, create_game_mode)
        self.states = {
            GameStateType.MENU: menu_state,
            GameStateType.PLAYING: PlayingState(self.screen_size),
            GameStateType.RESULTS: ResultsState(self.screen_size)
        }
        
        # Start with menu state
        self.current_state = menu_state

def main():
    """Run the test game."""
    # Initialize Pygame
    pygame.init()
    screen_size = (1280, 720)
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption("Hand Drawing Challenge - Test")
    
    # Create and initialize game
    game = TestGame(screen_size)
    game.initialize()
    game.start()
    
    # Game loop
    clock = pygame.time.Clock()
    running = True
    
    try:
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    game.handle_input(event)
            
            # Update game state
            delta_time = clock.get_time() / 1000.0  # Convert to seconds
            game.update(delta_time)
            
            # Draw
            game.draw()
            pygame.display.flip()
            
            # Cap frame rate
            clock.tick(60)
            
    finally:
        # Cleanup
        pygame.quit()

if __name__ == "__main__":
    main()

```

# test_harness.py

```py
# test_harness.py

import pygame
import sys
from game import create_game_mode
from game.base import GameConfig
from game.managers import CompetitiveGameManager
from ui.utils.colors import Colors
from typing import Dict, Optional, List

class GameTestHarness:
    """Test harness to demonstrate and test game functionality."""
    
    def __init__(self, width: int = 1280, height: int = 720):
        """Initialize the test harness.
        
        Args:
            width: Window width in pixels
            height: Window height in pixels
        """
        pygame.init()
        pygame.display.set_caption("Hand Drawing Challenge - Test Harness")
        
        self.screen_size = (width, height)
        self.screen = pygame.display.set_mode(self.screen_size)
        self.clock = pygame.time.Clock()
        
        # Font setup
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)
        
        # Game mode management
        self.current_mode = None
        self.game_config = GameConfig()
        
        # Player management for competitive mode
        self.competitive_manager = CompetitiveGameManager()
        
        # UI State
        self.show_player_dialog = False
        self.player_name_input = ""
        self.show_help = False
        
        # Create UI areas
        self.setup_ui_areas()
        
    def setup_ui_areas(self) -> None:
        """Set up UI button areas and regions."""
        button_height = 50
        button_width = 200
        spacing = 20
        
        # Main menu buttons
        self.buttons: Dict[str, pygame.Rect] = {
            'single_player': pygame.Rect(
                (self.screen_size[0] - button_width) // 2,
                200,
                button_width,
                button_height
            ),
            'competitive': pygame.Rect(
                (self.screen_size[0] - button_width) // 2,
                200 + button_height + spacing,
                button_width,
                button_height
            ),
            'add_player': pygame.Rect(
                (self.screen_size[0] - button_width) // 2,
                200 + (button_height + spacing) * 2,
                button_width,
                button_height
            ),
            'help': pygame.Rect(
                (self.screen_size[0] - button_width) // 2,
                200 + (button_height + spacing) * 3,
                button_width,
                button_height
            )
        }
        
        # Player name input dialog
        dialog_width = 400
        dialog_height = 200
        self.player_dialog_rect = pygame.Rect(
            (self.screen_size[0] - dialog_width) // 2,
            (self.screen_size[1] - dialog_height) // 2,
            dialog_width,
            dialog_height
        )
        
    def draw_button(self, rect: pygame.Rect, text: str, 
                    hovered: bool = False) -> None:
        """Draw a button with hover effect."""
        color = Colors.BUTTON_HOVER if hovered else Colors.BUTTON_NORMAL
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, Colors.BORDER, rect, 2)
        
        text_surface = self.font.render(text, True, Colors.TEXT)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)
        
    def draw_player_dialog(self) -> None:
        """Draw the add player dialog."""
        # Draw semi-transparent overlay
        overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        # Draw dialog box
        pygame.draw.rect(self.screen, Colors.BACKGROUND, self.player_dialog_rect)
        pygame.draw.rect(self.screen, Colors.BORDER, self.player_dialog_rect, 2)
        
        # Draw title
        title = self.font.render("Add New Player", True, Colors.TEXT)
        title_rect = title.get_rect(
            centerx=self.player_dialog_rect.centerx,
            top=self.player_dialog_rect.top + 20
        )
        self.screen.blit(title, title_rect)
        
        # Draw input field
        input_rect = pygame.Rect(
            self.player_dialog_rect.left + 20,
            self.player_dialog_rect.centery - 20,
            self.player_dialog_rect.width - 40,
            40
        )
        pygame.draw.rect(self.screen, Colors.BUTTON_NORMAL, input_rect)
        pygame.draw.rect(self.screen, Colors.BORDER, input_rect, 2)
        
        # Draw input text
        text_surface = self.font.render(self.player_name_input, True, Colors.TEXT)
        text_rect = text_surface.get_rect(
            midleft=(input_rect.left + 10, input_rect.centery)
        )
        self.screen.blit(text_surface, text_rect)
        
    def draw_help(self) -> None:
        """Draw help overlay with controls and information."""
        overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 192))
        self.screen.blit(overlay, (0, 0))
        
        help_text = [
            "Controls:",
            "SPACE - Toggle Drawing",
            "C - Clear Canvas",
            "ESC - Pause Game",
            "Q - Quit to Menu",
            "",
            "Player Management:",
            f"Current Players: {self.competitive_manager.get_player_count()}",
            "Add players before starting competitive mode"
        ]
        
        y_offset = 100
        for line in help_text:
            text = self.font.render(line, True, Colors.TEXT)
            rect = text.get_rect(
                centerx=self.screen_size[0] // 2,
                top=y_offset
            )
            self.screen.blit(text, rect)
            y_offset += 40
            
    def draw_player_list(self) -> None:
        """Draw the current list of players."""
        if self.competitive_manager.get_player_count() == 0:
            return
            
        y_offset = 400
        title = self.font.render("Current Players:", True, Colors.TEXT)
        title_rect = title.get_rect(
            centerx=self.screen_size[0] // 2,
            top=y_offset
        )
        self.screen.blit(title, title_rect)
        
        y_offset += 40
        for player in self.competitive_manager.players.values():
            text = self.font.render(f"• {player.name}", True, Colors.TEXT)
            rect = text.get_rect(
                centerx=self.screen_size[0] // 2,
                top=y_offset
            )
            self.screen.blit(text, rect)
            y_offset += 30
        
    def handle_input(self, event: pygame.event.Event) -> bool:
        """Handle input events.
        
        Returns:
            bool: False if the game should quit, True otherwise
        """
        if event.type == pygame.QUIT:
            return False
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not self.show_player_dialog and not self.show_help:
                mouse_pos = pygame.mouse.get_pos()
                for button_name, button_rect in self.buttons.items():
                    if button_rect.collidepoint(mouse_pos):
                        if button_name == 'single_player':
                            self.start_single_player()
                        elif button_name == 'competitive':
                            self.start_competitive()
                        elif button_name == 'add_player':
                            self.show_player_dialog = True
                        elif button_name == 'help':
                            self.show_help = True
            
        elif event.type == pygame.KEYDOWN:
            if self.show_player_dialog:
                if event.key == pygame.K_RETURN:
                    if self.player_name_input.strip():
                        self.competitive_manager.add_player(self.player_name_input.strip())
                        self.player_name_input = ""
                        self.show_player_dialog = False
                elif event.key == pygame.K_ESCAPE:
                    self.show_player_dialog = False
                    self.player_name_input = ""
                elif event.key == pygame.K_BACKSPACE:
                    self.player_name_input = self.player_name_input[:-1]
                else:
                    if len(self.player_name_input) < 20:  # Max name length
                        self.player_name_input += event.unicode
            elif self.show_help:
                if event.key == pygame.K_ESCAPE:
                    self.show_help = False
            elif self.current_mode:
                self.current_mode.handle_input(event)
                
        return True
        
    def start_single_player(self) -> None:
        """Start single player mode."""
        print("Starting single player mode...")  # Debug print
        try:
            self.current_mode = create_game_mode(
                "single_player",
                self.screen_size,
                self.game_config
            )
            if self.current_mode:
                # print("Game mode created successfully")  # Debug print
                # print("Initializing game mode...")  # Debug print
                # self.current_mode.initialize()
                print("Starting game mode...")  # Debug print
                self.current_mode.start()
                print("Single player mode started successfully")  # Debug print
        except Exception as e:
            print(f"Failed to start single player mode: {e}")
            import traceback
            traceback.print_exc()  # This will print the full error stack
            self.current_mode = None
            
    def start_competitive(self) -> None:
        """Start competitive mode if enough players."""
        if self.competitive_manager.get_player_count() < 2:
            print("Need at least 2 players for competitive mode!")
            return
            
        self.current_mode = create_game_mode(
            "competitive",
            self.screen_size,
            self.game_config
        )
        if self.current_mode:
            self.current_mode.initialize()
            self.current_mode.start()
            
    def run(self) -> None:
        """Main game loop."""
        running = True
        
        while running:
            # Handle events
            for event in pygame.event.get():
                running = self.handle_input(event)
                
            # Clear screen
            self.screen.fill(Colors.BACKGROUND)
            
            if self.current_mode:
                # Update and draw current game mode
                self.current_mode.update(self.clock.get_time() / 1000.0)
                self.current_mode.draw()
            else:
                # Draw menu
                title = self.title_font.render(
                    "Hand Drawing Challenge", True, Colors.TEXT)
                title_rect = title.get_rect(
                    centerx=self.screen_size[0] // 2,
                    top=50
                )
                self.screen.blit(title, title_rect)
                
                # Draw buttons
                mouse_pos = pygame.mouse.get_pos()
                for button_name, button_rect in self.buttons.items():
                    hovered = button_rect.collidepoint(mouse_pos)
                    self.draw_button(
                        button_rect,
                        button_name.replace('_', ' ').title(),
                        hovered
                    )
                
                # Draw player list
                self.draw_player_list()
            
            # Draw overlays
            if self.show_player_dialog:
                self.draw_player_dialog()
            elif self.show_help:
                self.draw_help()
            
            pygame.display.flip()
            self.clock.tick(60)
            
        pygame.quit()

def main():
    """Entry point for the test harness."""
    harness = GameTestHarness()
    harness.run()

if __name__ == "__main__":
    main()
```

# tests\__init__.py

```py
# This file makes the tests directory a Python package

```

# tests\test_competitive_mode.py

```py
# tests/test_competitive_mode.py
import pytest
from hand_drawing_challenge.game.managers import CompetitiveGameManager
from hand_drawing_challenge.game.managers.event_manager import GameEvent

class TestCompetitiveMode:
    @pytest.fixture
    def game_manager(self):
        return CompetitiveGameManager()
    
    def test_multiple_players(self, game_manager):
        # Add multiple players
        player_ids = [
            game_manager.add_player(f"Player {i}")
            for i in range(5)
        ]
        
        # Verify turn rotation
        first_rotation = [game_manager.next_turn() for _ in range(5)]
        assert first_rotation == player_ids
        
        # Verify wrapping
        assert game_manager.next_turn() == player_ids[0]
    
    def test_player_state_updates(self, game_manager):
        player_id = game_manager.add_player("Test Player")
        game_manager.update_player_score(player_id, 100)
        
        player_state = game_manager.players[player_id]
        assert player_state.score == 100
    
    def test_event_emission(self, game_manager):
        events_received = []
        
        def on_turn_changed(player_id, name):
            events_received.append(("turn_changed", player_id))
        
        game_manager.event_manager.subscribe(GameEvent.TURN_CHANGED, on_turn_changed)
        
        player_id = game_manager.add_player("Test Player")
        game_manager.next_turn()
        
        assert len(events_received) == 1
        assert events_received[0][0] == "turn_changed"
        assert events_received[0][1] == player_id
```

# tests\test_input_processing.py

```py
# tests/test_input_processing.py
import os
import sys
import unittest
import numpy as np
import cv2
from unittest.mock import Mock, patch

# Add project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from hand_drawing_challenge.input_processing.camera import Camera, CameraConfig, CameraError
from hand_drawing_challenge.input_processing.hand_tracking import HandTracker
from hand_drawing_challenge.input_processing.hand_tracking import HandPoint

class TestCamera(unittest.TestCase):
    """Test suite for Camera class."""
    
    def setUp(self):
        self.config = CameraConfig(
            width=640,
            height=480,
            fps=60,
            device_id=0
        )
    
    @patch('cv2.VideoCapture')
    def test_camera_initialization(self, mock_capture):
        """Test camera initialization."""
        mock_capture.return_value.isOpened.return_value = True
        
        camera = Camera(self.config)
        camera.start()
        
        # Verify camera was initialized with correct settings
        mock_capture.assert_called_once_with(self.config.device_id)
        mock_capture.return_value.set.assert_any_call(
            cv2.CAP_PROP_FRAME_WIDTH, self.config.width)
        mock_capture.return_value.set.assert_any_call(
            cv2.CAP_PROP_FRAME_HEIGHT, self.config.height)
        mock_capture.return_value.set.assert_any_call(
            cv2.CAP_PROP_FPS, self.config.fps)
    
    @patch('cv2.VideoCapture')
    def test_get_frame(self, mock_capture):
        """Test frame capture."""
        mock_capture.return_value.isOpened.return_value = True
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_capture.return_value.read.return_value = (True, test_frame)
        
        camera = Camera(self.config)
        camera.start()
        success, frame = camera.get_frame()
        
        self.assertTrue(success)
        self.assertEqual(frame.shape, (480, 640, 3))
    
    def test_context_manager(self):
        """Test camera context manager."""
        with patch('cv2.VideoCapture') as mock_capture:
            mock_capture.return_value.isOpened.return_value = True
            
            with Camera(self.config) as camera:
                self.assertTrue(camera._is_running)
            
            # Verify camera was released
            mock_capture.return_value.release.assert_called_once()

class TestHandTracker(unittest.TestCase):
    """Test suite for HandTracker class."""
    
    def setUp(self):
        # Don't create tracker in setUp since we need to pass mocked hands module
        pass
    
    @patch('mediapipe.solutions.hands')
    def test_get_index_finger_tip_no_hand(self, mock_mp_hands):
        """Test when no hand is detected."""
        # Setup mock with no hands detected
        mock_results = Mock()
        mock_results.multi_hand_landmarks = None
        mock_hands = Mock()
        mock_hands.process.return_value = mock_results
        mock_mp_hands.Hands.return_value = mock_hands
        
        # Create tracker with mocked hands module
        self.tracker = HandTracker(
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5,
            hands_module=mock_mp_hands
        )
        
        # Create empty test frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        point = self.tracker.get_index_finger_tip(test_frame)
        self.assertIsNone(point)
    
    @patch('mediapipe.solutions.hands')
    @patch('cv2.cvtColor')
    def test_get_index_finger_tip_with_hand(self, mock_cvtColor, mock_mp_hands):
        """Test when hand is detected."""
        # Create and configure the mock chain
        mock_hands = Mock()
        mock_mp_hands.Hands.return_value = mock_hands
        
        # Create the landmark with specific coordinates
        mock_landmark = Mock()
        mock_landmark.x = 0.5
        mock_landmark.y = 0.6
        mock_landmark.z = 0.1
        
        # Create landmarks list with the specific index finger tip
        landmarks_list = [Mock() for _ in range(21)]
        landmarks_list[8] = mock_landmark
        
        # Create hand landmarks with the landmarks list
        mock_hand_landmarks = Mock()
        mock_hand_landmarks.landmark = landmarks_list
        
        # Create results with the hand landmarks
        mock_results = Mock()
        mock_results.multi_hand_landmarks = [mock_hand_landmarks]
        
        # Set up the process method to return our mock results
        mock_hands.process = Mock(return_value=mock_results)
        
        # Create tracker with mocked hands module
        self.tracker = HandTracker(
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5,
            hands_module=mock_mp_hands
        )
        
        # Setup color conversion mock
        mock_cvtColor.return_value = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Create test frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Get finger position
        point = self.tracker.get_index_finger_tip(test_frame)
        
        self.assertIsNotNone(point)
        self.assertEqual(point.x, 0.5)
        self.assertEqual(point.y, 0.6)
        self.assertEqual(point.z, 0.1)

def main():
    unittest.main()

if __name__ == '__main__':
    main()

```

# tests\test_ui\__init__.py

```py

```

# tests\test_ui\test_canvas.py

```py
# tests/test_ui/test_canvas.py
import unittest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
import pygame
import cv2
from ui.components.canvas import DrawingCanvas
from input_processing.hand_tracking import HandPoint

class TestDrawingCanvas(unittest.TestCase):
    """Test suite for the DrawingCanvas component."""

    def setUp(self):
        """Set up test environment before each test."""
        # Initialize Pygame for testing
        pygame.init()
        
        # Create a test rectangle for the canvas
        self.test_rect = pygame.Rect(0, 0, 640, 480)
        
        # Create the canvas component
        self.canvas = DrawingCanvas(self.test_rect)
        
        # Create a test surface for drawing
        self.test_surface = pygame.Surface((640, 480))
        
        # Create a sample camera frame
        self.test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Create a sample hand point
        self.test_hand_point = HandPoint(x=0.5, y=0.5, z=0.0)

    def tearDown(self):
        """Clean up after each test."""
        pygame.quit()

    def test_initialization(self):
        """Test canvas initialization."""
        self.assertEqual(self.canvas.rect, self.test_rect)
        self.assertTrue(self.canvas.visible)
        self.assertFalse(self.canvas.is_drawing)
        self.assertEqual(self.canvas.canvas.shape, (480, 640, 3))

    def test_clear_canvas(self):
        """Test canvas clearing functionality."""
        # Draw something on the canvas first
        self.canvas.is_drawing = True
        self.canvas.update(self.test_frame, self.test_hand_point)
        
        # Clear the canvas
        self.canvas.clear()
        
        # Check if canvas is empty (all zeros)
        self.assertTrue(np.all(self.canvas.canvas == 0))
        self.assertEqual(len(self.canvas.drawing_tracker.get_trail_points()), 0)

    def test_drawing_state_toggle(self):
        """Test drawing state toggling."""
        initial_state = self.canvas.get_drawing_state()
        self.canvas.set_drawing_state(not initial_state)
        self.assertEqual(self.canvas.get_drawing_state(), not initial_state)

    @patch('cv2.circle')
    def test_update_with_hand_point(self, mock_circle):
        """Test canvas update with valid hand point."""
        # Set up drawing mode
        self.canvas.set_drawing_state(True)
        
        # Update canvas with hand point
        self.canvas.update(self.test_frame, self.test_hand_point)
        
        # Verify circle was drawn
        mock_circle.assert_called_once()

    def test_update_without_hand_point(self):
        """Test canvas update with no hand point."""
        # Make copy of canvas before update
        canvas_before = self.canvas.canvas.copy()
        
        # Update without hand point
        self.canvas.update(self.test_frame, None)
        
        # Verify canvas hasn't changed
        np.testing.assert_array_equal(self.canvas.canvas, canvas_before)

    @patch('pygame.draw.rect')
    def test_draw_method(self, mock_draw_rect):
        """Test the draw method."""
        # Test drawing when visible
        self.canvas.draw(self.test_surface)
        mock_draw_rect.assert_called_once()
        
        # Test drawing when not visible
        self.canvas.visible = False
        mock_draw_rect.reset_mock()
        self.canvas.draw(self.test_surface)
        mock_draw_rect.assert_not_called()

    def test_visibility_methods(self):
        """Test show/hide functionality."""
        self.canvas.hide()
        self.assertFalse(self.canvas.visible)
        
        self.canvas.show()
        self.assertTrue(self.canvas.visible)

    @patch('cv2.line')
    def test_drawing_trail(self, mock_line):
        """Test trail drawing functionality."""
        self.canvas.set_drawing_state(True)
        
        # Simulate multiple points for trail
        points = [
            HandPoint(x=0.3, y=0.3, z=0.0),
            HandPoint(x=0.4, y=0.4, z=0.0),
            HandPoint(x=0.5, y=0.5, z=0.0)
        ]
        
        # Update with each point
        for point in points:
            self.canvas.update(self.test_frame, point)
        
        # Verify lines were drawn (points - 1) times
        self.assertEqual(mock_line.call_count, len(points) - 1)

    def test_smoothing_functionality(self):
        """Test position smoothing functionality."""
        self.canvas.set_drawing_state(True)
        
        # Create a series of similar points to test smoothing
        points = [
            HandPoint(x=0.5, y=0.5, z=0.0),
            HandPoint(x=0.51, y=0.51, z=0.0),
            HandPoint(x=0.49, y=0.49, z=0.0),
            HandPoint(x=0.5, y=0.5, z=0.0)
        ]
        
        # Update with each point and collect smoothed positions
        smoothed_positions = []
        for point in points:
            self.canvas.update(self.test_frame, point)
            trail_points = self.canvas.drawing_tracker.get_trail_points()
            if trail_points:
                smoothed_positions.append(trail_points[-1])
        
        # Verify smoothed positions are stable (not too jittery)
        if len(smoothed_positions) >= 2:
            for i in range(1, len(smoothed_positions)):
                # Calculate distance between consecutive points
                x1, y1 = smoothed_positions[i-1]
                x2, y2 = smoothed_positions[i]
                distance = np.sqrt((x2-x1)**2 + (y2-y1)**2)
                # Ensure movement isn't too large
                self.assertLess(distance, 20)  # Adjust threshold as needed

if __name__ == '__main__':
    unittest.main()
```

# ui\__init__.py

```py

```

# ui\base.py

```py
# ui/base.py
from abc import ABC, abstractmethod
import pygame

class UIComponent(ABC):
    """Abstract base class for UI components."""
    
    def __init__(self, rect: pygame.Rect):
        """Initialize the UI component.
        
        Args:
            rect: The component's position and size
        """
        self.rect = rect
        self.visible = True
        
    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the component on the screen.
        
        Args:
            screen: Pygame surface to draw on
        """
        pass
        
    @abstractmethod
    def update(self, *args, **kwargs) -> None:
        """Update the component's state."""
        pass
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle an event.
        
        Args:
            event: Pygame event to handle
            
        Returns:
            bool: True if event was handled, False otherwise
        """
        return False
        
    def show(self) -> None:
        """Make the component visible."""
        self.visible = True
        
    def hide(self) -> None:
        """Make the component invisible."""
        self.visible = False
```

# ui\components\__init__.py

```py

```

# ui\components\canvas.py

```py
# ui/components/canvas.py
import cv2
import numpy as np
import pygame
from ..base import UIComponent
from ..utils.colors import Colors
from input_processing.drawing_tracker import DrawingTracker
from input_processing.hand_tracking import HandPoint

class DrawingCanvas(UIComponent):
    """Component for handling drawing visualization and input."""
    
    def __init__(self, rect: pygame.Rect):
        """Initialize the drawing canvas.
        
        Args:
            rect: Position and size of the canvas
        """
        super().__init__(rect)
        self.canvas = np.zeros((rect.height, rect.width, 3), dtype=np.uint8)
        self.drawing_tracker = DrawingTracker(width=rect.width, height=rect.height)
        self.is_drawing = False
        
    def update(self, camera_frame: np.ndarray, hand_point: HandPoint) -> None:
        """Update the canvas with new input.
        
        Args:
            camera_frame: Current camera frame
            hand_point: Current hand position
        """
        # Update drawing tracker and get smoothed position
        smoothed_pos = self.drawing_tracker.update(hand_point, self.is_drawing)
        
        if smoothed_pos:
            x, y = smoothed_pos
            # Draw current position indicator
            color = Colors.DRAWING_ACTIVE if self.is_drawing else Colors.DRAWING_INACTIVE
            cv2.circle(camera_frame, (x, y), 5, color, -1)
            
            # Draw trail
            trail_points = self.drawing_tracker.get_trail_points()
            if len(trail_points) > 1:
                cv2.line(self.canvas,
                       trail_points[-2],
                       trail_points[-1],
                       Colors.TRAIL_COLOR,
                       2)
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the canvas on the screen.
        
        Args:
            screen: Pygame surface to draw on
        """
        if not self.visible:
            return
            
        # Draw canvas border
        pygame.draw.rect(screen, Colors.BORDER, self.rect, 2)
        
        # Convert canvas to pygame surface
        canvas_surface = pygame.surfarray.make_surface(
            cv2.cvtColor(self.canvas, cv2.COLOR_BGR2RGB))
        canvas_surface = pygame.transform.rotate(canvas_surface, 270)
        
        # Draw to screen
        screen.blit(canvas_surface, self.rect)
    
    def clear(self) -> None:
        """Clear the drawing canvas."""
        self.drawing_tracker.clear()
        self.canvas = np.zeros((self.rect.height, self.rect.width, 3), dtype=np.uint8)
    
    def set_drawing_state(self, is_drawing: bool) -> None:
        """Set whether currently drawing or not.
        
        Args:
            is_drawing: Whether to enable drawing mode
        """
        self.is_drawing = is_drawing
    
    def get_drawing_state(self) -> bool:
        """Get current drawing state.
        
        Returns:
            bool: Whether currently in drawing mode
        """
        return self.is_drawing
```

# ui\components\pattern_display.py

```py
# ui/components/pattern_display.py
import pygame
from ..base import UIComponent
from ..utils.colors import Colors

class PatternDisplay(UIComponent):
    """Component for displaying the target pattern to draw."""
    
    def __init__(self, rect: pygame.Rect):
        """Initialize the pattern display.
        
        Args:
            rect: Position and size of the display
        """
        super().__init__(rect)
        self.pattern_surface = None
        self.title_font = pygame.font.Font(None, 36)
    
    def update(self, pattern_surface: pygame.Surface = None) -> None:
        """Update the pattern to display.
        
        Args:
            pattern_surface: New pattern to display
        """
        self.pattern_surface = pattern_surface
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the pattern display.
        
        Args:
            screen: Pygame surface to draw on
        """
        if not self.visible:
            return
            
        # Draw border
        pygame.draw.rect(screen, Colors.BORDER, self.rect, 2)
        
        # Draw title
        title = self.title_font.render("Pattern to Draw", True, Colors.TEXT)
        title_rect = title.get_rect(
            centerx=self.rect.centerx,
            top=self.rect.top - 40
        )
        screen.blit(title, title_rect)
        
        # Draw pattern if available
        if self.pattern_surface:
            pattern_rect = self.pattern_surface.get_rect(center=self.rect.center)
            screen.blit(self.pattern_surface, pattern_rect)
```

# ui\components\score_display.py

```py
# ui/components/score_display.py
import pygame
from typing import List, Tuple
from ..base import UIComponent
from ..utils.colors import Colors

class ScoreDisplay(UIComponent):
    """Component for displaying game stats and score."""
    
    def __init__(self, rect: pygame.Rect):
        """Initialize the score display.
        
        Args:
            rect: Position and size of the display
        """
        super().__init__(rect)
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 36)
        self.score = 0
        self.game_state = "waiting"
        self.is_drawing = False
    
    def update(self, score: int = None, game_state: str = None, 
               is_drawing: bool = None) -> None:
        """Update the display stats.
        
        Args:
            score: Current score
            game_state: Current game state
            is_drawing: Whether currently drawing
        """
        if score is not None:
            self.score = score
        if game_state is not None:
            self.game_state = game_state
        if is_drawing is not None:
            self.is_drawing = is_drawing
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the score display.
        
        Args:
            screen: Pygame surface to draw on
        """
        if not self.visible:
            return
            
        # Draw border and background
        pygame.draw.rect(screen, Colors.BORDER, self.rect, 2)
        
        # Draw title
        title = self.title_font.render("Game Stats", True, Colors.TEXT)
        title_rect = title.get_rect(
            centerx=self.rect.centerx,
            top=self.rect.top - 40
        )
        screen.blit(title, title_rect)
        
        # Draw stats
        stats = [
            f"Score: {self.score}",
            f"Status: {self.game_state}",
            f"Drawing: {'Yes' if self.is_drawing else 'No'}"
        ]
        
        y_offset = self.rect.top + 30
        for stat in stats:
            text = self.font.render(stat, True, Colors.TEXT)
            screen.blit(text, (self.rect.left + 20, y_offset))
            y_offset += 50
```

# ui\game_ui.py

```py
import pygame
import cv2
import numpy as np
from input_processing.camera import Camera, CameraConfig
from input_processing.hand_tracking import HandTracker
from input_processing.drawing_tracker import DrawingTracker

class GameUI:
    def __init__(self, width=1280, height=720):
        """Initialize the game UI.
        
        Args:
            width: Window width in pixels
            height: Window height in pixels
        """
        pygame.init()
        pygame.display.set_caption("Hand Drawing Challenge")
        
        # Set up display
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.BLUE = (0, 0, 255)
        self.GRAY = (128, 128, 128)
        
        # Set up game areas
        self.setup_layout()
        
        # Initialize camera with mirroring disabled by default
        camera_config = CameraConfig(mirror=False)
        self.camera = Camera(camera_config)
        self.tracker = HandTracker()
        self.drawing_tracker = DrawingTracker(width=640, height=480)
        self.is_drawing = False
        self.canvas = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Game state
        self.score = 0
        self.game_state = "waiting"  # waiting, playing, completed
        
        # Font setup
        self.font = pygame.font.Font(None, 36)
        
        # Start camera
        self.camera.start()
        
    def setup_layout(self):
        """Set up the game layout with different sections."""
        # Camera view area (center)
        self.camera_rect = pygame.Rect(320, 120, 640, 480)
        
        # Pattern area (left)
        self.pattern_rect = pygame.Rect(20, 120, 280, 280)
        
        # Stats area (right)
        self.stats_rect = pygame.Rect(980, 120, 280, 480)
        
        # Button areas
        button_y = 620
        self.start_button = pygame.Rect(480, button_y, 120, 40)
        self.clear_button = pygame.Rect(680, button_y, 120, 40)
        
    def draw_text(self, text, position, color=None):
        """Draw text on the screen."""
        if color is None:
            color = self.WHITE
        text_surface = self.font.render(text, True, color)
        self.screen.blit(text_surface, position)
        
    def draw_button(self, rect, text, color=None):
        """Draw a button with text."""
        if color is None:
            color = self.GRAY
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, self.WHITE, rect, 2)
        
        # Center text on button
        text_surface = self.font.render(text, True, self.WHITE)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)
        
    def update_camera_feed(self):
        """Update and display the camera feed."""
        success, frame = self.camera.get_frame()
        
        if success:
            # Frame is already mirrored if configured in camera_config
            
            # Process hand tracking
            hand_point = self.tracker.get_index_finger_tip(frame)
            
            # Update drawing tracker and get smoothed position
            smoothed_pos = self.drawing_tracker.update(hand_point, self.is_drawing)
            
            if smoothed_pos:
                x, y = smoothed_pos
                # Draw current position
                color = (0, 255, 0) if self.is_drawing else (0, 0, 255)
                cv2.circle(frame, (x, y), 5, color, -1)
                
                # Draw trail
                trail_points = self.drawing_tracker.get_trail_points()
                if len(trail_points) > 1:
                    cv2.line(self.canvas,
                           trail_points[-2],
                           trail_points[-1],
                           (0, 255, 0),
                           2)
            
            # Combine frame and canvas
            display = cv2.addWeighted(frame, 1.0, self.canvas, 0.7, 0)
            
            # Convert to pygame surface
            display = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
            display = pygame.surfarray.make_surface(display)
            display = pygame.transform.rotate(display, 270)
            
            # Draw to screen
            self.screen.blit(display, self.camera_rect)
        
    def draw(self):
        """Draw the game UI."""
        # Clear screen
        self.screen.fill(self.BLACK)
        
        # Draw main sections
        pygame.draw.rect(self.screen, self.GRAY, self.pattern_rect, 2)
        pygame.draw.rect(self.screen, self.GRAY, self.camera_rect, 2)
        pygame.draw.rect(self.screen, self.GRAY, self.stats_rect, 2)
        
        # Update camera feed
        self.update_camera_feed()
        
        # Draw section titles
        self.draw_text("Pattern to Draw", (20, 80))
        self.draw_text("Drawing Area", (320, 80))
        self.draw_text("Game Stats", (980, 80))
        
        # Draw stats
        stats_x = 1000
        self.draw_text(f"Score: {self.score}", (stats_x, 150))
        self.draw_text(f"Status: {self.game_state}", (stats_x, 200))
        self.draw_text("Drawing: " + ("Yes" if self.is_drawing else "No"), 
                      (stats_x, 250))
        
        # Draw buttons
        self.draw_button(self.start_button, "Start")
        self.draw_button(self.clear_button, "Clear")
        
    def handle_click(self, pos):
        """Handle mouse clicks."""
        if self.start_button.collidepoint(pos):
            self.start_game()
        elif self.clear_button.collidepoint(pos):
            self.clear_drawing()
            
    def start_game(self):
        """Start a new game."""
        self.game_state = "playing"
        self.clear_drawing()
        
    def clear_drawing(self):
        """Clear the drawing trail."""
        self.drawing_tracker.clear()
        self.canvas = np.zeros((480, 640, 3), dtype=np.uint8)
        
    def toggle_drawing(self):
        """Toggle drawing mode."""
        self.is_drawing = not self.is_drawing
        
    def run(self):
        """Main game loop."""
        running = True
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.toggle_drawing()
                    elif event.key == pygame.K_q:
                        running = False
            
            # Draw everything
            self.draw()
            
            # Update display
            pygame.display.flip()
            
            # Cap the frame rate
            self.clock.tick(60)
        
        # Cleanup
        self.cleanup()
        
    def cleanup(self):
        """Clean up resources."""
        self.camera.stop()
        pygame.quit()

def main():
    game = GameUI()
    game.run()

if __name__ == "__main__":
    main()

```

# ui\utils\__init__.py

```py

```

# ui\utils\colors.py

```py
from typing import Tuple

# Type alias for RGB colors
ColorRGB = Tuple[int, int, int]

class Colors:
    """Color constants for the UI."""
    
    # Basic colors
    BLACK: ColorRGB = (0, 0, 0)
    WHITE: ColorRGB = (255, 255, 255)
    RED: ColorRGB = (255, 0, 0)
    GREEN: ColorRGB = (0, 255, 0)
    BLUE: ColorRGB = (0, 0, 255)
    
    # UI colors
    BACKGROUND: ColorRGB = BLACK
    TEXT: ColorRGB = WHITE
    BORDER: ColorRGB = (128, 128, 128)  # Gray
    
    # Drawing colors
    DRAWING_ACTIVE: ColorRGB = GREEN
    DRAWING_INACTIVE: ColorRGB = RED
    TRAIL_COLOR: ColorRGB = (0, 255, 0)  # Green
    
    # Button colors
    BUTTON_NORMAL: ColorRGB = (128, 128, 128)  # Gray
    BUTTON_HOVER: ColorRGB = (160, 160, 160)  # Light Gray
    BUTTON_PRESSED: ColorRGB = (100, 100, 100)  # Dark Gray
```

# ui\visualization.py

```py
# ui/visualization.py
import cv2
import numpy as np
from collections import deque
from typing import Optional, Tuple
from input_processing.camera import Camera, CameraConfig
from input_processing.hand_tracking import HandTracker, HandPoint

class HandTrackingVisualizer:
    """Visualizes hand tracking with drawing capabilities and stability improvements."""
    
    def __init__(self, width: int = 640, height: int = 480, 
                 smoothing_window: int = 5,
                 min_detection_confidence: float = 0.7,
                 mirror: bool = True):
        """Initialize the visualizer with drawing canvas and stability settings.
        
        Args:
            width: Canvas width in pixels
            height: Canvas height in pixels
            smoothing_window: Number of frames to use for position smoothing
            min_detection_confidence: Minimum confidence for hand detection
            mirror: Whether to mirror the camera feed horizontally
        """
        self.width = width
        self.height = height
        self.canvas = np.zeros((height, width, 3), dtype=np.uint8)
        self.trail_points = []
        
        # Position smoothing
        self.smoothing_window = smoothing_window
        self.position_history = deque(maxlen=smoothing_window)
        self.last_valid_position: Optional[Tuple[int, int]] = None
        
        # Initialize camera and tracker
        self.camera = Camera(CameraConfig(width=width, height=height))
        self.tracker = HandTracker(min_detection_confidence=min_detection_confidence)
        
        # Drawing settings
        self.trail_color = (0, 255, 0)  # Green trail
        self.point_color = (0, 0, 255)  # Red point for current position
        self.trail_thickness = 4
        self.point_radius = 5
        
        # Camera settings
        self.mirror = mirror  # Mirror the camera feed
        self.is_mirrored = mirror  # Current mirror state
        
        # Drawing state
        self.is_drawing = False  # Whether we're currently recording the path
        
        # Stability settings
        self.max_jump_distance = 100  # Maximum allowed position change between frames
        self.min_movement_threshold = 5  # Minimum movement to register a new point
    
    def _smooth_position(self, new_point: Optional[HandPoint]) -> Optional[Tuple[int, int]]:
        """Smooth the hand position using a moving average and validate movement.
        
        Args:
            new_point: New hand position from tracker
            
        Returns:
            Smoothed and validated (x, y) position or None if invalid
        """
        if new_point is None:
            return self.last_valid_position
            
        # Convert normalized coordinates to pixel coordinates
        x = int(new_point.x * self.width)
        y = int(new_point.y * self.height)
        
        # Validate position is within bounds
        if not (0 <= x < self.width and 0 <= y < self.height):
            return self.last_valid_position
            
        # Check for unrealistic jumps if we have a previous position
        if self.last_valid_position:
            last_x, last_y = self.last_valid_position
            distance = np.sqrt((x - last_x)**2 + (y - last_y)**2)
            if distance > self.max_jump_distance:
                return self.last_valid_position
        
        # Add to position history
        self.position_history.append((x, y))
        
        # Calculate smoothed position
        if len(self.position_history) >= 3:  # Need at least 3 points for stable smoothing
            x_smooth = int(np.mean([p[0] for p in self.position_history]))
            y_smooth = int(np.mean([p[1] for p in self.position_history]))
            
            # Update last valid position
            self.last_valid_position = (x_smooth, y_smooth)
            return x_smooth, y_smooth
            
        return x, y
    
    def _should_add_point(self, new_position: Tuple[int, int]) -> bool:
        """Determine if a new point should be added to the trail.
        
        Args:
            new_position: New smoothed position
            
        Returns:
            True if point should be added, False otherwise
        """
        if not self.trail_points:
            return True
            
        last_x, last_y = self.trail_points[-1]
        new_x, new_y = new_position
        distance = np.sqrt((new_x - last_x)**2 + (new_y - last_y)**2)
        
        return distance >= self.min_movement_threshold
    
    def run(self):
        """Run the visualization loop."""
        try:
            self.camera.start()
            cv2.namedWindow('Hand Drawing')
            
            while True:
                # Get frame and process hand tracking
                success, frame = self.camera.get_frame()
                if not success:
                    continue
                    
                # Mirror the frame if needed
                if self.is_mirrored:
                    frame = cv2.flip(frame, 1)
                
                # Get finger position and smooth it
                hand_point = self.tracker.get_index_finger_tip(frame)
                smoothed_position = self._smooth_position(hand_point)
                
                if smoothed_position:
                    x, y = smoothed_position
                    
                    # Only add point if we're in drawing mode and movement is significant
                    if self.is_drawing and self._should_add_point((x, y)):
                        self.trail_points.append((x, y))
                        
                        # Draw trail
                        if len(self.trail_points) > 1:
                            cv2.line(self.canvas,
                                   self.trail_points[-2],
                                   self.trail_points[-1],
                                   self.trail_color,
                                   self.trail_thickness)
                    
                    # Always draw current position
                    point_color = (0, 255, 0) if self.is_drawing else (0, 0, 255)  # Green if drawing, red if not
                    cv2.circle(frame, (x, y), self.point_radius, point_color, -1)
                
                # Combine frame and canvas
                display = cv2.addWeighted(frame, 1.0, self.canvas, 0.7, 0)
                
                # Add status text
                status = []
                if not hand_point:
                    status.append("No Hand Detected")
                else:
                    status.append("Hand Detected")
                status.append("Recording" if self.is_drawing else "Not Recording")
                
                # Display status text
                y_offset = 30
                for text in status:
                    color = (0, 255, 0) if "Recording" in text or "Hand Detected" in text else (0, 0, 255)
                    cv2.putText(display, text, (10, y_offset), 
                              cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                    y_offset += 35
                
                cv2.imshow('Hand Drawing', display)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):  # Quit
                    break
                elif key == ord('c'):  # Clear canvas
                    self.canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)
                    self.trail_points = []
                elif key == ord('m'):  # Toggle mirror
                    self.is_mirrored = not self.is_mirrored
                    # Clear canvas when switching mirror mode to avoid confusion
                    self.canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)
                    self.trail_points = []
                elif key == 32:  # Spacebar - Toggle drawing
                    self.is_drawing = not self.is_drawing
                    # Start a new trail when starting to draw
                    if self.is_drawing:
                        self.trail_points = []
                
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        self.camera.stop()
        cv2.destroyAllWindows()
```

