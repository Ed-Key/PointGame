# file: tests/test_ui/test_manager.py

import pytest
import pygame
from unittest.mock import Mock, patch
from hand_drawing_challenge.events.bus import EventBus
from hand_drawing_challenge.events.types import GameEventType
from hand_drawing_challenge.ui.manager import UIManager
from hand_drawing_challenge.ui.base import UIComponent

@pytest.fixture
def event_bus():
    """Create a fresh event bus for testing."""
    return EventBus()

@pytest.fixture
def ui_manager(event_bus):
    """Create a UI manager with mocked pygame."""
    with patch('pygame.display.set_mode'), \
         patch('pygame.init'), \
         patch('pygame.display.set_caption'), \
         patch('pygame.font.init'), \
         patch('pygame.font.Font'):
        return UIManager(event_bus, screen_size=(1280, 720))

class TestUIManager:
    """Test suite for UIManager functionality."""
    
    def test_initialization(self, ui_manager):
        """Test UI manager initializes with correct components."""
        assert 'canvas' in ui_manager.components
        assert 'pattern' in ui_manager.components
        assert 'score' in ui_manager.components
        assert ui_manager.renderer is not None
    
    def test_component_visibility(self, ui_manager):
        """Test component visibility control."""
        # All components should be visible by default
        assert ui_manager.get_component('canvas').visible
        
        # Test visibility toggle
        ui_manager.set_component_visibility('canvas', False)
        assert not ui_manager.get_component('canvas').visible
        
        ui_manager.set_component_visibility('canvas', True)
        assert ui_manager.get_component('canvas').visible
    
    def test_update_calls_components(self, ui_manager):
        """Test that update calls update on all visible components."""
        # Replace all existing components with a mock
        mock_component = Mock(spec=UIComponent)
        mock_component.visible = True
        ui_manager.components = {'mock': mock_component}
        
        # Update UI manager
        delta_time = 0.016  # 60 FPS
        ui_manager.update(delta_time)
        
        # Verify component was updated
        mock_component.update.assert_called_once_with(delta_time)
    
    def test_render_calls_components(self, ui_manager):
        """Test that render calls draw on all visible components."""
        # Replace all existing components with a mock
        mock_component = Mock(spec=UIComponent)
        mock_component.visible = True
        ui_manager.components = {'mock': mock_component}
        
        # Create a mock surface
        mock_surface = Mock(spec=pygame.Surface)
        with patch.object(ui_manager.renderer, 'get_screen', return_value=mock_surface), \
             patch.object(ui_manager.renderer, 'present'):
            ui_manager.render()
        
        # Verify component was drawn with the mock surface
        mock_component.draw.assert_called_once_with(mock_surface)
    
    def test_game_end_cleanup(self, ui_manager, event_bus):
        """Test cleanup on game end event."""
        with patch.object(ui_manager.renderer, 'cleanup') as mock_cleanup:
            event_bus.publish(GameEventType.GAME_ENDED, None)
            mock_cleanup.assert_called_once()
    
    def test_get_nonexistent_component(self, ui_manager):
        """Test getting a component that doesn't exist."""
        assert ui_manager.get_component('nonexistent') is None
    
    def test_set_visibility_nonexistent_component(self, ui_manager):
        """Test setting visibility of nonexistent component doesn't raise error."""
        ui_manager.set_component_visibility('nonexistent', False)  # Should not raise
