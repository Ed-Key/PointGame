import pygame
import cv2
import numpy as np
from typing import Any, Tuple, Optional
from ..base import GameState, GameStateType
from ui.components.canvas import DrawingCanvas
from ui.components.pattern_display import PatternDisplay
from ui.components.score_display import ScoreDisplay
from ui.utils.colors import Colors
from input_processing.camera import Camera, CameraConfig, CameraError
from input_processing.hand_tracking import HandTracker, HandPoint
from input_processing.drawing_tracker import DrawingTracker

class PlayingState(GameState):
    """Game playing state handling."""
    
    def __init__(self, screen_size: Tuple[int, int]):
        """Initialize playing state."""
        super().__init__()
        print("Initializing PlayingState...") # Debug print
        
        self.screen_size = screen_size
        
        # Initialize components and input processing
        self.setup_ui_components()
        
        # Game state
        self.time_remaining = 60.0  # 60 seconds per round
        self.current_score = 0
        self.is_paused = False
        
        # Drawing state
        self.canvas = np.zeros((480, 640, 3), dtype=np.uint8)
        self.is_drawing = False
        
        # Font setup
        self.font = pygame.font.Font(None, 36)
        
        # Initialize trackers first
        print("Initializing trackers...") # Debug print
        self.tracker = HandTracker()
        self.drawing_tracker = DrawingTracker(width=640, height=480)
        
        # Initialize camera last
        print("Setting up camera...") # Debug print
        camera_config = CameraConfig(
            width=640,
            height=480,
            fps=30,
            mirror=False,
            device_id=0  # Explicitly set to use first camera
        )
        self.camera = Camera(camera_config)
        print("Camera object created") # Debug print
        
    def setup_ui_components(self) -> None:
        """Initialize UI components."""
        # Calculate component positions based on screen size
        canvas_size = (640, 480)
        pattern_size = (280, 280)
        score_size = (280, 480)
        
        # Center canvas horizontally
        canvas_x = (self.screen_size[0] - canvas_size[0]) // 2
        canvas_y = 120
        
        # Pattern display on left
        pattern_x = 20
        pattern_y = canvas_y
        
        # Score display on right
        score_x = self.screen_size[0] - score_size[0] - 20
        score_y = canvas_y
        
        # Create components
        self.canvas_rect = pygame.Rect(canvas_x, canvas_y, *canvas_size)
        self.pattern_display = PatternDisplay(
            pygame.Rect(pattern_x, pattern_y, *pattern_size)
        )
        self.score_display = ScoreDisplay(
            pygame.Rect(score_x, score_y, *score_size)
        )
    
    def on_enter(self) -> None:
        """Called when entering this state."""
        print("Entering playing state...") # Debug print
        try:
            if hasattr(self, 'camera'):
                print("Starting camera...") # Debug print
                self.camera.start()
                print("Camera started successfully") # Debug print
            else:
                print("No camera attribute found in on_enter") # Debug print
            
            # Reset game state
            self.time_remaining = 60.0
            self.current_score = 0
            self.is_paused = False
            self.is_drawing = False
            self.canvas = np.zeros((480, 640, 3), dtype=np.uint8)
            self.drawing_tracker.clear()
            
        except Exception as e:
            print(f"Error in on_enter: {e}")
            self.transition_to(GameStateType.MENU)
    
    def on_exit(self) -> None:
        """Called when exiting this state."""
        print("Exiting playing state...") # Debug print
        self.cleanup()
    
    def update_camera_feed(self) -> Optional[pygame.Surface]:
        """Update and display the camera feed."""
        try:
            if not hasattr(self, 'camera'):
                print("No camera attribute found") # Debug print
                return None
                
            if not self.camera._is_running:
                print("Camera exists but is not running") # Debug print
                return None
                
            success, frame = self.camera.get_frame()
            if not success:
                print("Failed to get camera frame") # Debug print
                return None
            
            # Process hand tracking
            hand_point = self.tracker.get_index_finger_tip(frame)
            
            # Update drawing tracker and get smoothed position
            smoothed_pos = self.drawing_tracker.update(hand_point, self.is_drawing)
            
            if smoothed_pos:
                x, y = smoothed_pos
                # Draw current position
                color = (0, 255, 0) if self.is_drawing else (0, 0, 255)
                cv2.circle(frame, (x, y), 5, color, -1)
                
                # Draw trail
                trail_points = self.drawing_tracker.get_trail_points()
                if len(trail_points) > 1:
                    cv2.line(self.canvas,
                           trail_points[-2],
                           trail_points[-1],
                           (0, 255, 0),
                           2)
            
            # Combine frame and canvas
            display = cv2.addWeighted(frame, 1.0, self.canvas, 0.7, 0)
            
            # Convert to pygame surface
            display = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
            display = pygame.surfarray.make_surface(display)
            display = pygame.transform.rotate(display, 270)
            
            return display
            
        except Exception as e:
            print(f"Error in update_camera_feed: {str(e)}") # Debug print
            return None
    
    def update(self, delta_time: float) -> None:
        """Update playing state."""
        if self.is_paused:
            return
            
        # Update time
        self.time_remaining -= delta_time
        if self.time_remaining <= 0:
            self.cleanup()
            self.transition_to(GameStateType.RESULTS)
            return
        
        # Update score display
        self.score_display.update(
            score=self.current_score,
            game_state="Playing",
            is_drawing=self.is_drawing
        )
    
    def draw(self) -> None:
        """Draw the playing state."""
        screen = pygame.display.get_surface()
        screen.fill(Colors.BACKGROUND)
        
        # Update and draw camera feed
        display = self.update_camera_feed()
        if display:
            screen.blit(display, self.canvas_rect)
        else:
            # Draw placeholder if camera feed isn't available
            pygame.draw.rect(screen, Colors.BUTTON_NORMAL, self.canvas_rect)
            no_camera_text = self.font.render("Camera not available", True, Colors.TEXT)
            text_rect = no_camera_text.get_rect(center=self.canvas_rect.center)
            screen.blit(no_camera_text, text_rect)
        
        # Draw UI components
        pygame.draw.rect(screen, Colors.BORDER, self.canvas_rect, 2)
        self.pattern_display.draw(screen)
        self.score_display.draw(screen)
        
        # Draw time remaining
        time_text = f"Time: {int(self.time_remaining)}s"
        time_surface = self.font.render(time_text, True, Colors.TEXT)
        screen.blit(time_surface, (20, 20))
        
        # Draw pause overlay if paused
        if self.is_paused:
            self._draw_pause_overlay(screen)
    
    def _draw_pause_overlay(self, screen: pygame.Surface) -> None:
        """Draw pause menu overlay."""
        overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        
        pause_text = self.font.render("PAUSED", True, Colors.TEXT)
        text_rect = pause_text.get_rect(center=(self.screen_size[0] // 2, 
                                              self.screen_size[1] // 2))
        
        screen.blit(overlay, (0, 0))
        screen.blit(pause_text, text_rect)
    
    def handle_input(self, event: Any) -> None:
        """Handle input events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.is_paused = not self.is_paused
            elif event.key == pygame.K_SPACE:
                self.is_drawing = not self.is_drawing
            elif event.key == pygame.K_c:
                self.canvas = np.zeros((480, 640, 3), dtype=np.uint8)
                self.drawing_tracker.clear()
            elif event.key == pygame.K_q and self.is_paused:
                self.cleanup()
                self.transition_to(GameStateType.MENU)
    
    def cleanup(self) -> None:
        """Clean up resources."""
        try:
            if hasattr(self, 'camera') and self.camera:
                print("Stopping camera...") # Debug print
                self.camera.stop()
                print("Camera stopped successfully") # Debug print
        except Exception as e:
            print(f"Error stopping camera: {e}")