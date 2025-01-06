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
