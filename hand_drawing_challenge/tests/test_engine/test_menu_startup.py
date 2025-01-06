# tests/test_engine/test_menu_startup.py

import pytest
from unittest.mock import Mock, patch
import pygame
from hand_drawing_challenge.engine.game_engine import GameEngine
from hand_drawing_challenge.events.bus import EventBus
from hand_drawing_challenge.engine.modes.menu_mode import MenuMode

@pytest.fixture(scope="session", autouse=True)
def pygame_init():
    """Initialize pygame for all tests."""
    pygame.init()
    yield
    pygame.quit()

@pytest.fixture
def event_bus():
    """Create a fresh event bus for each test."""
    return EventBus()

@pytest.fixture
def game_engine(event_bus):
    """Create a game engine instance for testing."""
    return GameEngine(event_bus)

@pytest.fixture
def mock_display():
    """Mock pygame display for testing."""
    with patch('pygame.display.set_mode') as mock_set_mode, \
         patch('pygame.display.get_surface') as mock_get_surface:
        # Create a mock surface
        mock_surface = Mock()
        mock_surface.get_rect.return_value = pygame.Rect(0, 0, 1280, 720)
        mock_set_mode.return_value = mock_surface
        mock_get_surface.return_value = mock_surface
        yield mock_set_mode

def test_engine_starts_with_menu_mode(game_engine, mock_display):
    """Test that the game engine starts in menu mode."""
    # Initialize the game engine
    game_engine.initialize()
    
    # Verify current mode is MenuMode
    assert game_engine.current_mode is not None
    assert isinstance(game_engine.current_mode, MenuMode)
    assert game_engine.current_mode.is_active

def test_menu_mode_initialization(game_engine, mock_display):
    """Test that menu mode is properly initialized."""
    game_engine.initialize()
    menu_mode = game_engine.current_mode
    
    # Verify menu mode state
    assert menu_mode.is_active
    assert menu_mode.event_bus is not None
    assert menu_mode.font_large is not None
    assert menu_mode.font_normal is not None
    assert menu_mode.buttons_initialized

def test_menu_mode_registers_events(event_bus, mock_display):
    """Test that menu mode properly registers for events."""
    menu_mode = MenuMode(event_bus)
    
    # Initialize and start menu mode
    menu_mode.initialize()
    menu_mode.start()
    
    # Verify menu is active
    assert menu_mode.is_active

def test_menu_mode_buttons_positioned(event_bus, mock_display):
    """Test that menu buttons are properly positioned."""
    menu_mode = MenuMode(event_bus)
    menu_mode.initialize()
    
    # Verify buttons are positioned within screen bounds
    assert 0 <= menu_mode.single_player_rect.centerx <= 1280
    assert 0 <= menu_mode.single_player_rect.centery <= 720
    assert 0 <= menu_mode.competitive_rect.centerx <= 1280
    assert 0 <= menu_mode.competitive_rect.centery <= 720
