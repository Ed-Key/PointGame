import pytest
from typing import Any
from unittest.mock import Mock, MagicMock
from hand_drawing_challenge.engine.game_engine import GameEngine
from hand_drawing_challenge.engine.modes.base_mode import GameMode
from hand_drawing_challenge.events.bus import EventBus
from hand_drawing_challenge.events.types import GameEventType

class MockGameMode(GameMode):
    """Mock implementation of GameMode for testing."""
    def __init__(self, event_bus: EventBus):
        super().__init__(event_bus)
        self.initialized = False
        self.started = False
        self.stopped = False
        self.updated = False
        self.last_delta = 0.0
    
    def initialize(self) -> None:
        self.initialized = True
    
    def start(self) -> None:
        self.started = True
        self.is_active = True
    
    def stop(self) -> None:
        self.stopped = True
        self.is_active = False
    
    def update(self, delta_time: float) -> None:
        self.updated = True
        self.last_delta = delta_time
    
    def handle_input(self, event: Any) -> None:
        """Handle input events."""
        pass

@pytest.fixture
def event_bus():
    """Create a fresh event bus for each test."""
    return EventBus()

@pytest.fixture
def game_engine(event_bus):
    """Create a fresh game engine for each test."""
    return GameEngine(event_bus)

@pytest.fixture
def mock_mode(event_bus):
    """Create a mock game mode for testing."""
    return MockGameMode(event_bus)

def test_initialization(game_engine):
    """Test initial game engine state."""
    assert not game_engine.is_running
    assert game_engine.current_mode is None
    assert game_engine.state_machine is not None

def test_engine_startup(game_engine):
    """Test engine initialization."""
    game_engine.initialize()
    assert game_engine.is_running

def test_change_mode(game_engine, mock_mode):
    """Test game mode switching."""
    game_engine.change_mode(mock_mode)
    
    assert game_engine.current_mode == mock_mode
    assert mock_mode.initialized
    assert mock_mode.started
    assert mock_mode.is_active

def test_change_mode_with_existing(game_engine, event_bus):
    """Test switching between modes."""
    first_mode = MockGameMode(event_bus)
    second_mode = MockGameMode(event_bus)
    
    game_engine.change_mode(first_mode)
    game_engine.change_mode(second_mode)
    
    assert game_engine.current_mode == second_mode
    assert first_mode.stopped
    assert not first_mode.is_active
    assert second_mode.started
    assert second_mode.is_active

def test_engine_update(game_engine, mock_mode):
    """Test engine update cycle."""
    game_engine.initialize()
    game_engine.change_mode(mock_mode)
    
    delta_time = 0.016
    game_engine.update(delta_time)
    
    assert mock_mode.updated
    assert mock_mode.last_delta == delta_time

def test_engine_update_when_stopped(game_engine, mock_mode):
    """Test update behavior when engine is not running."""
    game_engine.change_mode(mock_mode)
    
    game_engine.update(0.016)
    assert not mock_mode.updated  # Should not update when engine isn't running

def test_handle_game_end(game_engine, event_bus, mock_mode):
    """Test game end event handling."""
    game_engine.initialize()
    game_engine.change_mode(mock_mode)
    
    event_bus.publish(GameEventType.GAME_ENDED)
    
    assert not game_engine.is_running
    assert mock_mode.stopped

def test_event_subscription(game_engine, event_bus):
    """Test that engine properly subscribes to events."""
    # Check that the subscription was made during initialization
    assert GameEventType.GAME_ENDED in event_bus._subscribers
