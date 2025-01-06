# hand_drawing_challenge/events/events.py
from dataclasses import dataclass
from typing import Any
from .types import GameEventType

@dataclass
class BaseEvent:
    """Base class for all game events."""
    type: GameEventType
    data: Any = None

@dataclass
class InputEvent(BaseEvent):
    """Event for input-related updates."""
    pass

@dataclass
class GameStateEvent(BaseEvent):
    """Event for game state changes."""
    pass

@dataclass
class ScoreEvent(BaseEvent):
    """Event for score updates."""
    score: int
