# ui/game_ui.py
import pygame
import cv2
import numpy as np
from input_processing.camera import Camera, CameraConfig
from input_processing.hand_tracking import HandTracker
from .components.canvas import DrawingCanvas
from .components.pattern_display import PatternDisplay
from .components.score_display import ScoreDisplay
from .utils.colors import Colors

class GameUI:
    """Main game UI orchestrator."""
    
    def __init__(self, width=1280, height=720):
        """Initialize the game UI.
        
        Args:
            width: Window width in pixels
            height: Window height in pixels
        """
        pygame.init()
        pygame.display.set_caption("Hand Drawing Challenge")
        
        # Set up display
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        
        # Font setup
        self.font = pygame.font.Font(None, 36)
        
        # Initialize camera and tracking
        camera_config = CameraConfig(mirror=True)
        self.camera = Camera(camera_config)
        self.tracker = HandTracker()
        
        # Initialize UI components
        self.setup_components()
        
        # Game state
        self.score = 0
        self.game_state = "waiting"  # waiting, playing, completed
        
        # Start camera
        self.camera.start()
    
    def setup_components(self):
        """Set up UI components and their layouts."""
        # Camera view area (center)
        camera_rect = pygame.Rect(320, 120, 640, 480)
        self.canvas = DrawingCanvas(camera_rect)
        
        # Pattern area (left)
        pattern_rect = pygame.Rect(20, 120, 280, 280)
        self.pattern_display = PatternDisplay(pattern_rect)
        
        # Stats area (right)
        stats_rect = pygame.Rect(980, 120, 280, 480)
        self.score_display = ScoreDisplay(stats_rect)
        
        # Button areas
        button_y = 620
        self.start_button = pygame.Rect(480, button_y, 120, 40)
        self.clear_button = pygame.Rect(680, button_y, 120, 40)
    
    def draw_button(self, rect: pygame.Rect, text: str, color: Colors.ColorRGB = None):
        """Draw a button with text.
        
        Args:
            rect: Button rectangle
            text: Button text
            color: Button color (optional)
        """
        if color is None:
            color = Colors.BUTTON_NORMAL
            
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, Colors.BORDER, rect, 2)
        
        # Center text on button
        text_surface = self.font.render(text, True, Colors.TEXT)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)
    
    def handle_click(self, pos):
        """Handle mouse clicks.
        
        Args:
            pos: Click position (x, y)
        """
        if self.start_button.collidepoint(pos):
            self.start_game()
        elif self.clear_button.collidepoint(pos):
            self.clear_drawing()
    
    def start_game(self):
        """Start a new game."""
        self.game_state = "playing"
        self.score = 0
        self.clear_drawing()
    
    def clear_drawing(self):
        """Clear the drawing canvas."""
        self.canvas.clear()
    
    def toggle_drawing(self):
        """Toggle drawing mode."""
        current_state = self.canvas.get_drawing_state()
        self.canvas.set_drawing_state(not current_state)
    
    def update_components(self):
        """Update all UI components."""
        # Get camera frame and process hand tracking
        success, frame = self.camera.get_frame()
        
        if success:
            # Get hand position
            hand_point = self.tracker.get_index_finger_tip(frame)
            
            # Update canvas with new frame and hand position
            self.canvas.update(frame, hand_point)
            
            # Update score display
            self.score_display.update(
                score=self.score,
                game_state=self.game_state,
                is_drawing=self.canvas.get_drawing_state()
            )
            
            # Convert frame for display
            display = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            display = pygame.surfarray.make_surface(display)
            display = pygame.transform.rotate(display, 270)
            
            # Draw to screen at camera position
            self.screen.blit(display, self.canvas.rect)
    
    def draw(self):
        """Draw the game UI."""
        # Clear screen
        self.screen.fill(Colors.BACKGROUND)
        
        # Update and draw all components
        self.update_components()
        self.pattern_display.draw(self.screen)
        self.canvas.draw(self.screen)
        self.score_display.draw(self.screen)
        
        # Draw buttons
        self.draw_button(self.start_button, "Start")
        self.draw_button(self.clear_button, "Clear")
    
    def run(self):
        """Main game loop."""
        running = True
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.toggle_drawing()
                    elif event.key == pygame.K_q:
                        running = False
            
            # Draw everything
            self.draw()
            
            # Update display
            pygame.display.flip()
            
            # Cap the frame rate
            self.clock.tick(60)
        
        # Cleanup
        self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        self.camera.stop()
        pygame.quit()

def main():
    game = GameUI()
    game.run()

if __name__ == "__main__":
    main()