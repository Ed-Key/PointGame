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