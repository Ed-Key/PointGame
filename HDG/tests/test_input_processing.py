# tests/test_input_processing.py
import os
import sys
import unittest
import numpy as np
import cv2
from unittest.mock import Mock, patch

# Add project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from HDG.input_processing.camera import Camera, CameraConfig, CameraError
from HDG.input_processing.hand_tracking import HandTracker
from HDG.input_processing.hand_tracking import HandPoint

class TestCamera(unittest.TestCase):
    """Test suite for Camera class."""
    
    def setUp(self):
        self.config = CameraConfig(
            width=640,
            height=480,
            fps=60,
            device_id=0
        )
    
    @patch('cv2.VideoCapture')
    def test_camera_initialization(self, mock_capture):
        """Test camera initialization."""
        mock_capture.return_value.isOpened.return_value = True
        
        camera = Camera(self.config)
        camera.start()
        
        # Verify camera was initialized with correct settings
        mock_capture.assert_called_once_with(self.config.device_id)
        mock_capture.return_value.set.assert_any_call(
            cv2.CAP_PROP_FRAME_WIDTH, self.config.width)
        mock_capture.return_value.set.assert_any_call(
            cv2.CAP_PROP_FRAME_HEIGHT, self.config.height)
        mock_capture.return_value.set.assert_any_call(
            cv2.CAP_PROP_FPS, self.config.fps)
    
    @patch('cv2.VideoCapture')
    def test_get_frame(self, mock_capture):
        """Test frame capture."""
        mock_capture.return_value.isOpened.return_value = True
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_capture.return_value.read.return_value = (True, test_frame)
        
        camera = Camera(self.config)
        camera.start()
        success, frame = camera.get_frame()
        
        self.assertTrue(success)
        self.assertEqual(frame.shape, (480, 640, 3))
    
    def test_context_manager(self):
        """Test camera context manager."""
        with patch('cv2.VideoCapture') as mock_capture:
            mock_capture.return_value.isOpened.return_value = True
            
            with Camera(self.config) as camera:
                self.assertTrue(camera._is_running)
            
            # Verify camera was released
            mock_capture.return_value.release.assert_called_once()

class TestHandTracker(unittest.TestCase):
    """Test suite for HandTracker class."""
    
    def setUp(self):
        # Don't create tracker in setUp since we need to pass mocked hands module
        pass
    
    @patch('mediapipe.solutions.hands')
    def test_get_index_finger_tip_no_hand(self, mock_mp_hands):
        """Test when no hand is detected."""
        # Setup mock with no hands detected
        mock_results = Mock()
        mock_results.multi_hand_landmarks = None
        mock_hands = Mock()
        mock_hands.process.return_value = mock_results
        mock_mp_hands.Hands.return_value = mock_hands
        
        # Create tracker with mocked hands module
        self.tracker = HandTracker(
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5,
            hands_module=mock_mp_hands
        )
        
        # Create empty test frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        point = self.tracker.get_index_finger_tip(test_frame)
        self.assertIsNone(point)
    
    @patch('mediapipe.solutions.hands')
    @patch('cv2.cvtColor')
    def test_get_index_finger_tip_with_hand(self, mock_cvtColor, mock_mp_hands):
        """Test when hand is detected."""
        # Create and configure the mock chain
        mock_hands = Mock()
        mock_mp_hands.Hands.return_value = mock_hands
        
        # Create the landmark with specific coordinates
        mock_landmark = Mock()
        mock_landmark.x = 0.5
        mock_landmark.y = 0.6
        mock_landmark.z = 0.1
        
        # Create landmarks list with the specific index finger tip
        landmarks_list = [Mock() for _ in range(21)]
        landmarks_list[8] = mock_landmark
        
        # Create hand landmarks with the landmarks list
        mock_hand_landmarks = Mock()
        mock_hand_landmarks.landmark = landmarks_list
        
        # Create results with the hand landmarks
        mock_results = Mock()
        mock_results.multi_hand_landmarks = [mock_hand_landmarks]
        
        # Set up the process method to return our mock results
        mock_hands.process = Mock(return_value=mock_results)
        
        # Create tracker with mocked hands module
        self.tracker = HandTracker(
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5,
            hands_module=mock_mp_hands
        )
        
        # Setup color conversion mock
        mock_cvtColor.return_value = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Create test frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Get finger position
        point = self.tracker.get_index_finger_tip(test_frame)
        
        self.assertIsNotNone(point)
        self.assertEqual(point.x, 0.5)
        self.assertEqual(point.y, 0.6)
        self.assertEqual(point.z, 0.1)

def main():
    unittest.main()

if __name__ == '__main__':
    main()
