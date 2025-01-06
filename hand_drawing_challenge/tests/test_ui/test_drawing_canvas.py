# tests/test_ui/test_drawing_canvas.py

import pytest
import pygame
import numpy as np
from unittest.mock import Mock
from typing import Optional, Tuple

from hand_drawing_challenge.ui.components.canvas import DrawingCanvas
from hand_drawing_challenge.input.input_types import HandPoint

class TestDrawingCanvas:
    """
    Test the DrawingCanvas UI component that renders hand drawing visualization.
    
    This test suite verifies:
    1. Basic canvas initialization and rendering
    2. Hand tracking updates and drawing visualization
    3. Drawing trail management
    """
    
    @pytest.fixture
    def mock_rect(self):
        """Create a mock pygame Rect for testing."""
        return pygame.Rect(0, 0, 800, 600)
    
    @pytest.fixture
    def drawing_canvas(self, mock_rect):
        """Create DrawingCanvas instance for testing."""
        return DrawingCanvas(mock_rect)
    
    def test_initialization(self, drawing_canvas, mock_rect):
        """Verify canvas initializes correctly."""
        assert drawing_canvas.rect == mock_rect
        assert drawing_canvas.canvas.shape == (mock_rect.height, mock_rect.width, 3)
        assert not drawing_canvas.is_drawing
        assert drawing_canvas.last_position is None
    
    def test_update_with_hand_point(self, drawing_canvas):
        """Test canvas updates with hand position."""
        # Create mock camera frame
        frame = np.zeros((600, 800, 3), dtype=np.uint8)
        # Create hand point with normalized coordinates (0-1)
        hand_point = HandPoint(x=0.5, y=0.5, z=0.0)  # Center of the frame
        
        drawing_canvas.update(frame, hand_point)
        
        # Should have updated last position
        assert drawing_canvas.last_position is not None
        assert drawing_canvas.current_frame is not None
    
    def test_drawing_trail(self, drawing_canvas):
        """Test trail rendering when drawing is active."""
        # Create frame and hand point
        frame = np.zeros((600, 800, 3), dtype=np.uint8)
        hand_point = HandPoint(x=0.5, y=0.5, z=0.0)
        
        # Enable drawing
        drawing_canvas.set_drawing_state(True)
        assert drawing_canvas.get_drawing_state() is True
        
        # Simulate movement with normalized coordinates
        positions = [(0.5, 0.5), (0.51, 0.51), (0.52, 0.52)]
        for x, y in positions:
            hand_point = HandPoint(x=x, y=y, z=0.0)
            drawing_canvas.update(frame, hand_point)
            
        # Verify canvas has been updated
        assert np.any(drawing_canvas.canvas != 0)  # Canvas should have some drawing
    
    def test_clear_canvas(self, drawing_canvas):
        """Test canvas clearing."""
        # Create frame and hand point
        frame = np.zeros((600, 800, 3), dtype=np.uint8)
        hand_point = HandPoint(x=0.5, y=0.5, z=0.0)
        drawing_canvas.set_drawing_state(True)
        drawing_canvas.update(frame, hand_point)
        
        # Then clear
        drawing_canvas.clear()
        assert np.all(drawing_canvas.canvas == 0)  # Canvas should be cleared
        assert drawing_canvas.last_position is None
