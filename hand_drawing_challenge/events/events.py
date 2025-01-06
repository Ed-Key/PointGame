# events/events.py
from dataclasses import dataclass
from typing import Optional
from .types import GameEventType
from hand_drawing_challenge.services.patterns.models import Pattern
from hand_drawing_challenge.engine.state_machine import GameState

@dataclass(frozen=True)
class BaseEvent:
    type: GameEventType

@dataclass(frozen=True)
class GameStateChangedEvent(BaseEvent):
    new_state: GameState
    old_state: Optional[GameState] = None
    type: GameEventType = GameEventType.GAME_STARTED

@dataclass(frozen=True)
class ModeChangedEvent(BaseEvent):
    new_mode: str
    old_mode: Optional[str] = None
    type: GameEventType = GameEventType.GAME_MODE_SELECTED

@dataclass(frozen=True)
class ScoreEvent(BaseEvent):
    score: int
    player_id: Optional[str] = None
    type: GameEventType = GameEventType.SCORE_UPDATED

@dataclass(frozen=True)
class PatternGeneratedEvent(BaseEvent):
    pattern: Pattern
    type: GameEventType = GameEventType.PATTERN_GENERATED

@dataclass(frozen=True)
class PatternCompletedEvent(BaseEvent):
    pattern: Pattern
    score: float
    type: GameEventType = GameEventType.PATTERN_COMPLETED
