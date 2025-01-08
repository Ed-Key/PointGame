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