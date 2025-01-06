# tests/test_input/test_manager.py
import pytest
from unittest.mock import Mock, patch
from hand_drawing_challenge.input.manager import InputManager
from hand_drawing_challenge.input.interfaces import InputProcessor
from hand_drawing_challenge.events.bus import EventBus
from hand_drawing_challenge.events.types import GameEventType

class MockProcessor(InputProcessor):
    def __init__(self):
        self.processed = False
        self._active = True
        self.cleaned_up = False
    
    def process(self, *args, **kwargs):
        self.processed = True
    
    def is_active(self):
        return self._active
    
    def cleanup(self):
        self.cleaned_up = True

class TestInputManager:
    @pytest.fixture
    def event_bus(self):
        return Mock(spec=EventBus)
    
    @pytest.fixture
    def input_manager(self, event_bus):
        return InputManager(event_bus)
    
    def test_register_processor(self, input_manager):
        processor = MockProcessor()
        input_manager.register_processor("test", processor)
        assert "test" in input_manager.processors
    
    def test_process_input_calls_active_processors(self, input_manager):
        processor = MockProcessor()
        input_manager.register_processor("test", processor)
        
        input_manager.process_input()
        assert processor.processed
    
    def test_cleanup_calls_processor_cleanup(self, input_manager):
        processor = MockProcessor()
        input_manager.register_processor("test", processor)
        
        input_manager.cleanup()
        assert processor.cleaned_up
    
    def test_game_end_triggers_cleanup(self, input_manager, event_bus):
        processor = MockProcessor()
        input_manager.register_processor("test", processor)
        
        # Simulate game end event
        for handler in event_bus.subscribe.call_args_list:
            event_type, callback = handler[0]
            if event_type == GameEventType.GAME_ENDED:
                callback(GameEventType.GAME_ENDED)
                break
        
        assert processor.cleaned_up