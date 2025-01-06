# src/events/types.py

from enum import Enum, auto
from typing import Any, Callable, Dict, List, Union

class GameEventType(Enum):
    """Game event types for the event system."""
    # Input events
    HAND_DETECTED = auto()
    HAND_LOST = auto()
    HAND_POSITION_UPDATED = auto()
    DRAWING_STARTED = auto()
    DRAWING_ENDED = auto()
    CAMERA_FAILURE = auto()  # Added this event

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
    PATTERN_COMPLETED = auto()

    # Pattern events
    PATTERN_GENERATED = auto()  # New pattern is generated/selected
    PATTERN_DISPLAY_UPDATED = auto()  # Pattern display needs updating
    PATTERN_VALIDATION_STARTED = auto()  # Start validating a drawn pattern
    PATTERN_VALIDATION_COMPLETED = auto()  # Pattern validation is complete

EventHandler = Callable[[GameEventType, Any], None]