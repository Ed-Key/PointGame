# tests/test_input/test_hand_tracking_processor.py

import pytest
import numpy as np
import cv2
from unittest.mock import Mock, patch, PropertyMock
from hand_drawing_challenge.input.processors.hand_tracking import (
    HandTrackingProcessor,
    HandProcessorConfig
)
from hand_drawing_challenge.events.types import GameEventType
from hand_drawing_challenge.events.bus import EventBus

@pytest.fixture
def mock_event_bus():
    return Mock(spec=EventBus)

@pytest.fixture
def test_frame():
    """Create a test frame."""
    return np.zeros((480, 640, 3), dtype=np.uint8)

@pytest.fixture
def mock_camera(test_frame):
    """Create a mock camera that returns proper frame data."""
    with patch('cv2.VideoCapture') as mock:
        camera_instance = Mock()
        camera_instance.isOpened.return_value = True
        camera_instance.read.return_value = (True, test_frame)
        mock.return_value = camera_instance
        return mock

def create_mock_hands():
    """Create a mock MediaPipe hands object."""
    mock_hands = Mock()
    mock_process = Mock()
    mock_hands.process = mock_process
    return mock_hands

@pytest.fixture
def mock_mediapipe(request):
    """Create a mock MediaPipe hands module."""
    with patch('mediapipe.solutions.hands') as mock_mp:
        mock_hands = create_mock_hands()
        mock_mp.Hands.return_value = mock_hands
        mock_mp.HAND_CONNECTIONS = []
        return mock_mp

@pytest.fixture
def config():
    """Create test configuration."""
    return HandProcessorConfig(
        camera_width=640,
        camera_height=480,
        camera_id=0,
        mirror_camera=True,
        draw_debug=True
    )

@pytest.fixture
def processor(mock_event_bus, mock_camera, mock_mediapipe, config, test_frame):
    """Create processor with mocked dependencies."""
    with patch('cv2.cvtColor', return_value=test_frame):
        processor = HandTrackingProcessor(mock_event_bus, config)
        return processor

def create_mock_hand_landmarks(x=0.5, y=0.5, z=0.0):
    """Create mock hand landmarks."""
    landmark = Mock()
    landmark.x = x
    landmark.y = y
    landmark.z = z
    
    landmarks = [Mock() for _ in range(21)]
    landmarks[8] = landmark  # Index fingertip
    hand_landmarks = Mock()
    hand_landmarks.landmark = landmarks
    return hand_landmarks

def test_initialization(processor, config):
    """Test initial state."""
    assert processor.event_bus is not None
    assert processor.config == config
    assert not processor.is_active()
    assert not processor.hand_detected
    assert not processor.is_drawing

def test_start_stop(processor):
    """Test start/stop functionality."""
    processor.start()
    assert processor.is_active()
    
    processor.stop()
    assert not processor.is_active()

def test_process_hand_detected(processor, mock_event_bus, test_frame):
    """Test hand detection."""
    processor.start()
    
    # Setup hand detection result
    mock_results = Mock()
    hand_landmarks = create_mock_hand_landmarks()
    mock_results.multi_hand_landmarks = [hand_landmarks]
    processor.hands.process = Mock(return_value=mock_results)
    
    with patch('cv2.cvtColor', return_value=test_frame):
        processor.process()
    
    mock_event_bus.publish.assert_any_call(GameEventType.HAND_DETECTED)

def test_process_hand_lost(processor, mock_event_bus, test_frame):
    """Test hand lost detection."""
    processor.start()
    processor.hand_detected = True
    
    # Setup no hands detected
    mock_results = Mock()
    mock_results.multi_hand_landmarks = None
    processor.hands.process = Mock(return_value=mock_results)
    
    with patch('cv2.cvtColor', return_value=test_frame):
        processor.process()
    
    mock_event_bus.publish.assert_called_with(GameEventType.HAND_LOST)
    assert not processor.hand_detected

# def test_camera_failure(processor, mock_camera, test_frame):
#     """Test camera failure handling."""
#     # Configure mock camera to simulate failure
#     camera_instance = mock_camera.return_value
#     camera_instance.read.return_value = (False, None)
#     camera_instance.isOpened.return_value = False
    
#     processor.start()
#     result = processor.process()
        
#     assert result is None
#     assert not processor.is_active()

def test_drawing_update(processor, test_frame):
    """Test drawing functionality."""
    processor.start()
    processor.is_drawing = True
    
    # Setup hand detection with movement
    mock_results = Mock()
    hand_landmarks = create_mock_hand_landmarks()
    mock_results.multi_hand_landmarks = [hand_landmarks]
    processor.hands.process = Mock(return_value=mock_results)
    
    with patch('cv2.cvtColor', return_value=test_frame), \
         patch('cv2.line') as mock_line:
        # Process multiple frames
        for i in range(3):
            hand_landmarks.landmark[8].x = 0.5 + (i * 0.1)  # Move finger
            processor.process()
        
        assert mock_line.called

def test_mirror_configuration(processor, test_frame):
    """Test mirror configuration."""
    processor.start()
    
    # Test with mirroring enabled
    processor.config.mirror_camera = True
    with patch('cv2.cvtColor', return_value=test_frame), \
         patch('cv2.flip', return_value=test_frame) as mock_flip:
        processor.process()
        assert mock_flip.called
    
    # Test with mirroring disabled
    processor.config.mirror_camera = False
    with patch('cv2.cvtColor', return_value=test_frame), \
         patch('cv2.flip', return_value=test_frame) as mock_flip:
        processor.process()
        assert not mock_flip.called

def test_debug_visualization(processor, test_frame):
    """Test debug visualization."""
    processor.start()
    processor.config.draw_debug = True
    
    # Setup hand detection
    mock_results = Mock()
    mock_results.multi_hand_landmarks = [create_mock_hand_landmarks()]
    processor.hands.process = Mock(return_value=mock_results)
    
    with patch('cv2.cvtColor', return_value=test_frame), \
         patch('cv2.circle') as mock_circle:
        processor.process()
        assert mock_circle.called

def test_clear_canvas(processor):
    """Test canvas clearing."""
    processor.start()
    
    # Add content to canvas
    processor.canvas.fill(255)
    processor.drawing_tracker.trail_points = [(0, 0), (1, 1)]
    
    processor.clear_canvas()
    assert np.all(processor.canvas == 0)
    assert len(processor.drawing_tracker.get_trail_points()) == 0

def test_inactive_processor(processor):
    """Test inactive processor behavior."""
    result = processor.process()
    assert result is None
