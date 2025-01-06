# hand_drawing_challenge/ui/game_ui.py

import pygame
import cv2
from typing import Optional

from ..events.bus import EventBus
from ..events.types import GameEventType
from ..input.manager import InputManager
from ..input.processors.hand_tracking import HandTrackingProcessor, HandProcessorConfig
from .components.canvas import DrawingCanvas
from .components.pattern_display import PatternDisplay
from .components.score_display import ScoreDisplay
from .utils.colors import Colors

class GameUI:
    """
    Main UI orchestrator that integrates all visual components and input handling.
    
    This class coordinates:
    - Window management and rendering
    - Component layout and updates
    - Camera and hand tracking integration
    - Event dispatching
    """
    
    def __init__(self, width: int = 1280, height: int = 720):
        pygame.init()
        pygame.display.set_caption("Hand Drawing Challenge")
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        
        # Initialize event system
        self.event_bus = EventBus()
        
        # Initialize input processing
        self.setup_input_processing()
        
        # Create UI Components
        self.setup_ui_components()
        
        # Game state
        self.is_running = False
        self.current_score = 0
        
    def setup_input_processing(self) -> None:
        """Initialize input processing."""
        # Initialize input manager with event bus
        self.input_manager = InputManager(self.event_bus)
        
        # Initialize and register hand tracking processor
        hand_tracking_config = HandProcessorConfig(
            camera_width=640,
            camera_height=480,
            mirror_camera=False,
            draw_debug=True
        )
        self.hand_tracker = HandTrackingProcessor(self.event_bus, hand_tracking_config)
        self.input_manager.register_processor('hand_tracking', self.hand_tracker)
        
        # Start the hand tracker
        self.hand_tracker.start()
        
    def setup_ui_components(self) -> None:
        """Initialize and position all UI components."""
        # Main drawing area (center)
        self.drawing_canvas = DrawingCanvas(
            pygame.Rect(320, 120, 640, 480)
        )
        
        # Pattern display (left)
        self.pattern_display = PatternDisplay(
            pygame.Rect(20, 120, 280, 280)
        )
        
        # Score display (right)
        self.score_display = ScoreDisplay(
            pygame.Rect(980, 120, 280, 480)
        )
    
    def handle_input(self) -> None:
        """Process all user input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_running = False
                elif event.key == pygame.K_SPACE:
                    new_drawing_state = not self.drawing_canvas.get_drawing_state()
                    self.drawing_canvas.set_drawing_state(new_drawing_state)
                    # Get hand tracking processor and update its state
                    hand_tracker = self.input_manager.get_processor('hand_tracking')
                    if hand_tracker:
                        hand_tracker.set_drawing_state(new_drawing_state)
                elif event.key == pygame.K_c:
                    self.drawing_canvas.clear()
                    # Also clear the hand tracking processor's canvas
                    hand_tracker = self.input_manager.get_processor('hand_tracking')
                    if hand_tracker:
                        hand_tracker.clear_canvas()
    
    def update(self) -> None:
        """Update game state and all components."""
        # Process input first to update frame
        self.input_manager.process_input()
        
        # Get the processed frame
        frame = self.input_manager.get_frame()
        if frame is not None:
            self.drawing_canvas.update(frame)
            self.score_display.update(
                score=self.current_score,
                game_state="Drawing" if self.drawing_canvas.get_drawing_state() else "Ready",
                is_drawing=self.drawing_canvas.get_drawing_state()
            )
    
    def draw(self) -> None:
        """Render the current frame."""
        # Clear screen
        self.screen.fill(Colors.BACKGROUND)
        
        # Draw UI components
        self.drawing_canvas.draw(self.screen)
        self.pattern_display.draw(self.screen)
        self.score_display.draw(self.screen)
        
        # Draw instructions
        self._draw_instructions()
        
        # Update display
        pygame.display.flip()
        
    def _draw_instructions(self) -> None:
        """Draw control instructions."""
        instructions = [
            "SPACE - Toggle Drawing",
            "C - Clear Canvas",
            "ESC - Quit"
        ]
        
        font = pygame.font.Font(None, 36)
        y = 20
        for text in instructions:
            surface = font.render(text, True, Colors.TEXT)
            self.screen.blit(surface, (20, y))
            y += 30
    
    def run(self) -> None:
        """Main UI loop."""
        self.is_running = True
        
        try:
            # Start input processing
            self.input_manager.start()
            
            # Main loop
            while self.is_running:
                self.handle_input()
                self.update()
                self.draw()
                self.clock.tick(60)
                
        finally:
            self.cleanup()
    
    def cleanup(self) -> None:
        """Clean up resources."""
        self.input_manager.stop()
        pygame.quit()
