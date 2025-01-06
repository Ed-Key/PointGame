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
