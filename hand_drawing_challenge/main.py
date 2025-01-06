# main.py

import pygame
import sys
from hand_drawing_challenge.application.game_application import GameApplication
from hand_drawing_challenge.application.config import GameConfig

def main():
    """Application entry point."""
    try:
        # Initialize pygame
        pygame.init()
        
        # Create configuration
        config = GameConfig(
            screen_size=(1280, 720),
            fps=60,
            debug_mode=True,
            camera_device=0,
            camera_width=640,
            camera_height=480
        )
        
        # Create and start application
        app = GameApplication(config)
        app.start()
        
    except Exception as e:
        print(f"Error running application: {e}")
        sys.exit(1)
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()