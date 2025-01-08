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