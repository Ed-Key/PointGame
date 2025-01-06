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