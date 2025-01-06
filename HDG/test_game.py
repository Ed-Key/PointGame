import pygame
from game.base import GameMode, GameConfig, GameStateType
from game import create_game_mode
from game.states.menu_state import MenuState
from game.states.playing_state import PlayingState
from game.states.results_state import ResultsState

class TestGame(GameMode):
    """Test implementation of GameMode to verify state transitions."""
    
    def __init__(self, screen_size=(1280, 720)):
        """Initialize test game.
        
        Args:
            screen_size: Window size in pixels
        """
        config = GameConfig()  # Use default config for testing
        super().__init__(config)
        self.screen_size = screen_size
        
    def initialize(self) -> None:
        """Initialize game states."""
        # Create all game states
        # Create states with mode factory
        menu_state = MenuState(self.screen_size, create_game_mode)
        self.states = {
            GameStateType.MENU: menu_state,
            GameStateType.PLAYING: PlayingState(self.screen_size),
            GameStateType.RESULTS: ResultsState(self.screen_size)
        }
        
        # Start with menu state
        self.current_state = menu_state

def main():
    """Run the test game."""
    # Initialize Pygame
    pygame.init()
    screen_size = (1280, 720)
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption("Hand Drawing Challenge - Test")
    
    # Create and initialize game
    game = TestGame(screen_size)
    game.initialize()
    game.start()
    
    # Game loop
    clock = pygame.time.Clock()
    running = True
    
    try:
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    game.handle_input(event)
            
            # Update game state
            delta_time = clock.get_time() / 1000.0  # Convert to seconds
            game.update(delta_time)
            
            # Draw
            game.draw()
            pygame.display.flip()
            
            # Cap frame rate
            clock.tick(60)
            
    finally:
        # Cleanup
        pygame.quit()

if __name__ == "__main__":
    main()
