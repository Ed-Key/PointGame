# ui/visualization.py
# HandTrack visualizer file to help with drawing and stability improvements
import cv2
import numpy as np
from collections import deque
from typing import Optional, Tuple
from input_processing.camera import Camera, CameraConfig
from input_processing.hand_tracking import HandTracker, HandPoint

class HandTrackingVisualizer:
    """Visualizes hand tracking with drawing capabilities and stability improvements."""
    
    def __init__(self, width: int = 640, height: int = 480, 
                 smoothing_window: int = 5,
                 min_detection_confidence: float = 0.7,
                 mirror: bool = True):
        """Initialize the visualizer with drawing canvas and stability settings.
        
        Args:
            width: Canvas width in pixels
            height: Canvas height in pixels
            smoothing_window: Number of frames to use for position smoothing
            min_detection_confidence: Minimum confidence for hand detection
            mirror: Whether to mirror the camera feed horizontally
        """
        self.width = width
        self.height = height
        self.canvas = np.zeros((height, width, 3), dtype=np.uint8)
        self.trail_points = []
        
        # Position smoothing
        self.smoothing_window = smoothing_window
        self.position_history = deque(maxlen=smoothing_window)
        self.last_valid_position: Optional[Tuple[int, int]] = None
        
        # Initialize camera and tracker
        self.camera = Camera(CameraConfig(width=width, height=height))
        self.tracker = HandTracker(min_detection_confidence=min_detection_confidence)
        
        # Drawing settings
        self.trail_color = (0, 255, 0)  # Green trail
        self.point_color = (0, 0, 255)  # Red point for current position
        self.trail_thickness = 4
        self.point_radius = 5
        
        # Camera settings
        self.mirror = mirror  # Mirror the camera feed
        self.is_mirrored = mirror  # Current mirror state
        
        # Drawing state
        self.is_drawing = False  # Whether we're currently recording the path
        
        # Stability settings
        self.max_jump_distance = 100  # Maximum allowed position change between frames
        self.min_movement_threshold = 5  # Minimum movement to register a new point
    
    def _smooth_position(self, new_point: Optional[HandPoint]) -> Optional[Tuple[int, int]]:
        """Smooth the hand position using a moving average and validate movement.
        
        Args:
            new_point: New hand position from tracker
            
        Returns:
            Smoothed and validated (x, y) position or None if invalid
        """
        if new_point is None:
            return self.last_valid_position
            
        # Convert normalized coordinates to pixel coordinates
        x = int(new_point.x * self.width)
        y = int(new_point.y * self.height)
        
        # Validate position is within bounds
        if not (0 <= x < self.width and 0 <= y < self.height):
            return self.last_valid_position
            
        # Check for unrealistic jumps if we have a previous position
        if self.last_valid_position:
            last_x, last_y = self.last_valid_position
            distance = np.sqrt((x - last_x)**2 + (y - last_y)**2)
            if distance > self.max_jump_distance:
                return self.last_valid_position
        
        # Add to position history
        self.position_history.append((x, y))
        
        # Calculate smoothed position
        if len(self.position_history) >= 3:  # Need at least 3 points for stable smoothing
            x_smooth = int(np.mean([p[0] for p in self.position_history]))
            y_smooth = int(np.mean([p[1] for p in self.position_history]))
            
            # Update last valid position
            self.last_valid_position = (x_smooth, y_smooth)
            return x_smooth, y_smooth
            
        return x, y
    
    def _should_add_point(self, new_position: Tuple[int, int]) -> bool:
        """Determine if a new point should be added to the trail.
        
        Args:
            new_position: New smoothed position
            
        Returns:
            True if point should be added, False otherwise
        """
        if not self.trail_points:
            return True
            
        last_x, last_y = self.trail_points[-1]
        new_x, new_y = new_position
        distance = np.sqrt((new_x - last_x)**2 + (new_y - last_y)**2)
        
        return distance >= self.min_movement_threshold
    
    def run(self):
        """Run the visualization loop."""
        try:
            self.camera.start()
            cv2.namedWindow('Hand Drawing')
            
            while True:
                # Get frame and process hand tracking
                success, frame = self.camera.get_frame()
                if not success:
                    continue
                    
                # Mirror the frame if needed
                if self.is_mirrored:
                    frame = cv2.flip(frame, 1)
                
                # Get finger position and smooth it
                hand_point = self.tracker.get_index_finger_tip(frame)
                smoothed_position = self._smooth_position(hand_point)
                
                if smoothed_position:
                    x, y = smoothed_position
                    
                    # Only add point if we're in drawing mode and movement is significant
                    if self.is_drawing and self._should_add_point((x, y)):
                        self.trail_points.append((x, y))
                        
                        # Draw trail
                        if len(self.trail_points) > 1:
                            cv2.line(self.canvas,
                                   self.trail_points[-2],
                                   self.trail_points[-1],
                                   self.trail_color,
                                   self.trail_thickness)
                    
                    # Always draw current position
                    point_color = (0, 255, 0) if self.is_drawing else (0, 0, 255)  # Green if drawing, red if not
                    cv2.circle(frame, (x, y), self.point_radius, point_color, -1)
                
                # Combine frame and canvas
                display = cv2.addWeighted(frame, 1.0, self.canvas, 0.7, 0)
                
                # Add status text
                status = []
                if not hand_point:
                    status.append("No Hand Detected")
                else:
                    status.append("Hand Detected")
                status.append("Recording" if self.is_drawing else "Not Recording")
                
                # Display status text
                y_offset = 30
                for text in status:
                    color = (0, 255, 0) if "Recording" in text or "Hand Detected" in text else (0, 0, 255)
                    cv2.putText(display, text, (10, y_offset), 
                              cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                    y_offset += 35
                
                cv2.imshow('Hand Drawing', display)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):  # Quit
                    break
                elif key == ord('c'):  # Clear canvas
                    self.canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)
                    self.trail_points = []
                elif key == ord('m'):  # Toggle mirror
                    self.is_mirrored = not self.is_mirrored
                    # Clear canvas when switching mirror mode to avoid confusion
                    self.canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)
                    self.trail_points = []
                elif key == 32:  # Spacebar - Toggle drawing
                    self.is_drawing = not self.is_drawing
                    # Start a new trail when starting to draw
                    if self.is_drawing:
                        self.trail_points = []
                
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        self.camera.stop()
        cv2.destroyAllWindows()