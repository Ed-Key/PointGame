# tests/test_engine/test_game_startup.py

import pytest
from unittest.mock import Mock, patch
import pygame
from hand_drawing_challenge.application.game_application import GameApplication
from hand_drawing_challenge.engine.modes.menu_mode import MenuMode

@pytest.fixture
def mock_pygame():
    """Mock pygame initialization."""
    pygame.init()  # Initialize pygame
    pygame.font.init()  # Initialize font system
    
    # Create a real surface for testing
    test_surface = pygame.Surface((1280, 720))
    
    with patch('pygame.display.set_mode', return_value=test_surface) as mock_set_mode, \
         patch('pygame.display.get_surface', return_value=test_surface), \
         patch('pygame.time.Clock'), \
         patch('pygame.event.get', return_value=[]), \
         patch('hand_drawing_challenge.ui.manager.UIManager.render'), \
         patch('hand_drawing_challenge.ui.manager.UIManager.update_frame'), \
         patch('hand_drawing_challenge.input.manager.InputManager.start'), \
         patch('hand_drawing_challenge.input.manager.InputManager.process_input'), \
         patch('hand_drawing_challenge.input.manager.InputManager.get_frame', return_value=None):
        
        yield mock_set_mode
    
    pygame.font.quit()
    pygame.quit()

@pytest.fixture
def game_app(mock_pygame):
    """Create a game application instance for testing."""
    return GameApplication()

def test_application_starts_with_menu(game_app, mock_pygame):
    """Test that the game application starts with menu mode."""
    # Start the application in test mode
    game_app.start(test_mode=True)
    
    # Verify engine is initialized with menu mode
    assert game_app.engine.current_mode is not None
    assert isinstance(game_app.engine.current_mode, MenuMode)
    assert game_app.engine.current_mode.is_active

def test_full_startup_sequence(game_app, mock_pygame):
    """Test the complete startup sequence."""
    game_app.start(test_mode=True)
    
    # Verify all systems are initialized
    assert game_app.is_running
    assert game_app.engine.is_running
    assert isinstance(game_app.engine.current_mode, MenuMode)
    assert game_app.engine.current_mode.is_active
    assert game_app.event_bus is not None

def test_menu_mode_cleanup_on_stop(game_app, mock_pygame):
    """Test that menu mode is properly cleaned up when game stops."""
    game_app.start(test_mode=True)
    menu_mode = game_app.engine.current_mode
    
    # Stop the game
    game_app.stop()
    
    # Verify cleanup
    assert not game_app.is_running
    assert not menu_mode.is_active

@patch('pygame.event.get')
def test_menu_handles_events(mock_event_get, game_app, mock_pygame):
    """Test that menu mode properly handles events."""
    # Setup mock events
    mock_event = Mock()
    mock_event.type = pygame.MOUSEBUTTONDOWN
    mock_event.pos = (640, 360)  # Center of screen
    mock_event_get.return_value = [mock_event]
    
    game_app.start(test_mode=True)
    menu_mode = game_app.engine.current_mode
    
    # Process one frame
    game_app._process_frame()
    
    # Verify event was processed
    assert menu_mode.is_active
