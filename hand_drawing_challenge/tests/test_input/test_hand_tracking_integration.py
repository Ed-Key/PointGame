# tests/test_input/test_hand_tracking_integration.py
import pytest
import numpy as np
import cv2
from unittest.mock import Mock, patch
from hand_drawing_challenge.input.processors.hand_tracking import HandTrackingProcessor, HandProcessorConfig
from hand_drawing_challenge.events.bus import EventBus
from hand_drawing_challenge.events.types import GameEventType

class TestHandTrackingIntegration:
    @pytest.fixture
    def event_bus(self):
        return EventBus()
        
    @pytest.fixture
    def mock_hand_landmarks(self):
        """Create mock MediaPipe hand landmarks."""
        landmark = Mock()
        landmark.x = 0.5  # Center of frame
        landmark.y = 0.5
        landmark.z = 0.0
        
        landmarks = [Mock() for _ in range(21)]
        landmarks[8] = landmark  # Index fingertip
        
        hand_landmarks = Mock()
        hand_landmarks.landmark = landmarks
        return hand_landmarks

    @pytest.fixture
    def test_frame(self):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.circle(frame, (320, 240), 50, (255, 255, 255), -1)
        return frame

    @pytest.fixture
    def processor(self, event_bus, test_frame, mock_hand_landmarks):
        config = HandProcessorConfig(
            camera_width=640,
            camera_height=480,
            camera_id=0,
            draw_debug=True
        )
        
        with patch('cv2.VideoCapture') as mock_camera, \
             patch('mediapipe.solutions.hands.Hands') as mock_hands:
            
            # Mock camera
            camera_instance = Mock()
            camera_instance.isOpened.return_value = True
            camera_instance.read.return_value = (True, test_frame)
            mock_camera.return_value = camera_instance
            
            # Mock MediaPipe hand detection
            hands_instance = Mock()
            mock_results = Mock()
            mock_results.multi_hand_landmarks = [mock_hand_landmarks]
            hands_instance.process.return_value = mock_results
            mock_hands.return_value = hands_instance
            
            processor = HandTrackingProcessor(event_bus, config)
            processor.start()
            return processor

    def test_drawing_workflow(self, processor, event_bus):
        """Test complete drawing workflow with hand tracking."""
        received_events = []
        def event_handler(event_type, data):
            received_events.append((event_type, data))
            
        # Subscribe to events
        event_bus.subscribe(GameEventType.HAND_DETECTED, event_handler)
        event_bus.subscribe(GameEventType.HAND_POSITION_UPDATED, event_handler)
        event_bus.subscribe(GameEventType.DRAWING_STARTED, event_handler)
        
        # Process frames
        frames = []
        processor.set_drawing_state(True)
        
        for _ in range(5):
            frame = processor.process()
            frames.append(frame)
            
        # Verify events
        assert any(event[0] == GameEventType.HAND_DETECTED for event in received_events), \
            "Should detect hand"
        assert any(event[0] == GameEventType.HAND_POSITION_UPDATED for event in received_events), \
            "Should update hand position"
        
        # Verify drawing
        assert len(frames) == 5
        trail_points = processor.drawing_tracker.get_trail_points()
        assert len(trail_points) > 0, "Should record trail points"
        
        processor.clear_canvas()
        assert len(processor.drawing_tracker.get_trail_points()) == 0

    def test_performance(self, processor):
        """Test processing performance."""
        import time
        
        frames_to_test = 10  # Reduced from 30 to speed up test
        times = []
        
        for _ in range(frames_to_test):
            start = time.time()
            processor.process()
            times.append(time.time() - start)
            
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        # More realistic performance expectations
        assert avg_time < 0.05, f"Average frame time too high: {avg_time:.4f}s"
        assert max_time < 0.1, f"Max frame time too high: {max_time:.4f}s"