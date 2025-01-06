# tests/test_ui/test_canvas.py
import unittest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
import pygame
import cv2
from ui.components.canvas import DrawingCanvas
from input_processing.hand_tracking import HandPoint

class TestDrawingCanvas(unittest.TestCase):
    """Test suite for the DrawingCanvas component."""

    def setUp(self):
        """Set up test environment before each test."""
        # Initialize Pygame for testing
        pygame.init()
        
        # Create a test rectangle for the canvas
        self.test_rect = pygame.Rect(0, 0, 640, 480)
        
        # Create the canvas component
        self.canvas = DrawingCanvas(self.test_rect)
        
        # Create a test surface for drawing
        self.test_surface = pygame.Surface((640, 480))
        
        # Create a sample camera frame
        self.test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Create a sample hand point
        self.test_hand_point = HandPoint(x=0.5, y=0.5, z=0.0)

    def tearDown(self):
        """Clean up after each test."""
        pygame.quit()

    def test_initialization(self):
        """Test canvas initialization."""
        self.assertEqual(self.canvas.rect, self.test_rect)
        self.assertTrue(self.canvas.visible)
        self.assertFalse(self.canvas.is_drawing)
        self.assertEqual(self.canvas.canvas.shape, (480, 640, 3))

    def test_clear_canvas(self):
        """Test canvas clearing functionality."""
        # Draw something on the canvas first
        self.canvas.is_drawing = True
        self.canvas.update(self.test_frame, self.test_hand_point)
        
        # Clear the canvas
        self.canvas.clear()
        
        # Check if canvas is empty (all zeros)
        self.assertTrue(np.all(self.canvas.canvas == 0))
        self.assertEqual(len(self.canvas.drawing_tracker.get_trail_points()), 0)

    def test_drawing_state_toggle(self):
        """Test drawing state toggling."""
        initial_state = self.canvas.get_drawing_state()
        self.canvas.set_drawing_state(not initial_state)
        self.assertEqual(self.canvas.get_drawing_state(), not initial_state)

    @patch('cv2.circle')
    def test_update_with_hand_point(self, mock_circle):
        """Test canvas update with valid hand point."""
        # Set up drawing mode
        self.canvas.set_drawing_state(True)
        
        # Update canvas with hand point
        self.canvas.update(self.test_frame, self.test_hand_point)
        
        # Verify circle was drawn
        mock_circle.assert_called_once()

    def test_update_without_hand_point(self):
        """Test canvas update with no hand point."""
        # Make copy of canvas before update
        canvas_before = self.canvas.canvas.copy()
        
        # Update without hand point
        self.canvas.update(self.test_frame, None)
        
        # Verify canvas hasn't changed
        np.testing.assert_array_equal(self.canvas.canvas, canvas_before)

    @patch('pygame.draw.rect')
    def test_draw_method(self, mock_draw_rect):
        """Test the draw method."""
        # Test drawing when visible
        self.canvas.draw(self.test_surface)
        mock_draw_rect.assert_called_once()
        
        # Test drawing when not visible
        self.canvas.visible = False
        mock_draw_rect.reset_mock()
        self.canvas.draw(self.test_surface)
        mock_draw_rect.assert_not_called()

    def test_visibility_methods(self):
        """Test show/hide functionality."""
        self.canvas.hide()
        self.assertFalse(self.canvas.visible)
        
        self.canvas.show()
        self.assertTrue(self.canvas.visible)

    @patch('cv2.line')
    def test_drawing_trail(self, mock_line):
        """Test trail drawing functionality."""
        self.canvas.set_drawing_state(True)
        
        # Simulate multiple points for trail
        points = [
            HandPoint(x=0.3, y=0.3, z=0.0),
            HandPoint(x=0.4, y=0.4, z=0.0),
            HandPoint(x=0.5, y=0.5, z=0.0)
        ]
        
        # Update with each point
        for point in points:
            self.canvas.update(self.test_frame, point)
        
        # Verify lines were drawn (points - 1) times
        self.assertEqual(mock_line.call_count, len(points) - 1)

    def test_smoothing_functionality(self):
        """Test position smoothing functionality."""
        self.canvas.set_drawing_state(True)
        
        # Create a series of similar points to test smoothing
        points = [
            HandPoint(x=0.5, y=0.5, z=0.0),
            HandPoint(x=0.51, y=0.51, z=0.0),
            HandPoint(x=0.49, y=0.49, z=0.0),
            HandPoint(x=0.5, y=0.5, z=0.0)
        ]
        
        # Update with each point and collect smoothed positions
        smoothed_positions = []
        for point in points:
            self.canvas.update(self.test_frame, point)
            trail_points = self.canvas.drawing_tracker.get_trail_points()
            if trail_points:
                smoothed_positions.append(trail_points[-1])
        
        # Verify smoothed positions are stable (not too jittery)
        if len(smoothed_positions) >= 2:
            for i in range(1, len(smoothed_positions)):
                # Calculate distance between consecutive points
                x1, y1 = smoothed_positions[i-1]
                x2, y2 = smoothed_positions[i]
                distance = np.sqrt((x2-x1)**2 + (y2-y1)**2)
                # Ensure movement isn't too large
                self.assertLess(distance, 20)  # Adjust threshold as needed

if __name__ == '__main__':
    unittest.main()