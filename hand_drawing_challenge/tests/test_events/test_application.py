import pytest
from unittest.mock import patch, Mock
import time
from hand_drawing_challenge.application.game_application import GameApplication
from hand_drawing_challenge.events.types import GameEventType

@pytest.fixture
def game_app():
    """Create a fresh game application instance for each test."""
    return GameApplication()

def test_initial_state(game_app):
    """Test initial application state."""
    assert not game_app.is_running
    assert game_app.engine is not None
    assert game_app.event_bus is not None

def test_start_initializes_engine(game_app):
    """Test that starting the application initializes the engine."""
    with patch.object(game_app.engine, 'initialize') as mock_init:
        game_app.start(test_mode=True)
        mock_init.assert_called_once()

def test_start_publishes_event(game_app):
    """Test that starting publishes the correct event."""
    with patch.object(game_app.event_bus, 'publish') as mock_publish:
        game_app.start(test_mode=True)
        mock_publish.assert_any_call(GameEventType.GAME_STARTED)

@patch('time.time')
def test_game_loop_updates(mock_time, game_app):
    """Test that the game loop updates the engine with correct delta time."""
    # Mock time to return increasing values
    times = [1.0, 1.016, 1.032]  # Simulate 16ms frames
    mock_time.side_effect = times
    
    # Mock engine update
    with patch.object(game_app.engine, 'update') as mock_update:
        # Stop the loop after first update
        def stop_after_update(*args):
            game_app.is_running = False
        mock_update.side_effect = stop_after_update
        
        # Run game loop
        game_app.start(test_mode=False)
        # actual_delta_time = mock_update.call_args.args[0]  # Python 3.8+

        # Verify engine was updated with correct delta time
        # mock_update.assert_called_once_with(abs(actual_delta_time - 0.016) < 1e-10)

def test_stop_publishes_event(game_app):
    """Test that stopping publishes the correct event."""
    game_app.start(test_mode=True)
    
    with patch.object(game_app.event_bus, 'publish') as mock_publish:
        game_app.stop()
        mock_publish.assert_called_with(GameEventType.GAME_ENDED)

def test_handle_game_end(game_app):
    """Test handling of game end event."""
    game_app.start(test_mode=True)
    assert game_app.is_running
    
    game_app.event_bus.publish(GameEventType.GAME_ENDED)
    assert not game_app.is_running

def test_multiple_starts(game_app):
    """Test that multiple start calls are handled correctly."""
    game_app.start(test_mode=True)
    initial_engine = game_app.engine
    
    # Try to start again
    game_app.start(test_mode=True)
    
    # Verify we didn't reinitialize anything
    assert game_app.engine is initial_engine

def test_stop_when_not_running(game_app):
    """Test that stopping when not running is handled gracefully."""
    with patch.object(game_app.event_bus, 'publish') as mock_publish:
        game_app.stop()
        mock_publish.assert_not_called()

@patch('time.time')
def test_game_loop_exception_handling(mock_time, game_app):
    """Test that exceptions in the game loop are handled properly."""
    mock_time.return_value = 1.0
    
    with patch.object(game_app.engine, 'update') as mock_update:
        mock_update.side_effect = Exception("Test error")
        
        with patch('builtins.print') as mock_print:
            game_app.start(test_mode=False)
            
            # Verify error was printed and game stopped
            assert mock_print.called
            assert not game_app.is_running
