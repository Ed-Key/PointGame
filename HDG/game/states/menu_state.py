import pygame
from typing import Any, List, Tuple, Optional, Callable
from ..base import GameState, GameStateType, GameMode
from ui.utils.colors import Colors

class MenuItem:
    """Represents a clickable menu item."""
    
    def __init__(self, text: str, position: Tuple[int, int], action: Callable[[], None]):
        """Initialize menu item.
        
        Args:
            text: Text to display
            position: (x, y) position to render
            action: Game state to transition to when clicked
        """
        self.text = text
        self.position = position
        self.action = action
        self.font = pygame.font.Font(None, 48)
        self.is_hovered = False
        
        # Create text surfaces for normal and hover states
        self.text_normal = self.font.render(text, True, Colors.TEXT)
        self.text_hover = self.font.render(text, True, Colors.TEXT)
        
        # Create rect for collision detection
        self.rect = self.text_normal.get_rect(center=position)
    
    def update(self, mouse_pos: Tuple[int, int]) -> None:
        """Update hover state based on mouse position.
        
        Args:
            mouse_pos: Current mouse position
        """
        self.is_hovered = self.rect.collidepoint(mouse_pos)
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the menu item.
        
        Args:
            screen: Surface to draw on
        """
        text_surface = self.text_hover if self.is_hovered else self.text_normal
        screen.blit(text_surface, self.rect)

class MenuState(GameState):
    """Game menu state handling."""
    
    def __init__(self, screen_size: Tuple[int, int], mode_factory=None):
        """Initialize menu state.
        
        Args:
            screen_size: (width, height) of game window
            mode_factory: Callback to create game modes
        """
        super().__init__()
        self.screen_size = screen_size
        self.background_color = Colors.BACKGROUND
        self.items: List[MenuItem] = []
        self.current_mode: Optional[GameMode] = None
        self.mode_factory = mode_factory

        self.setup_menu_items()
        
        # Title setup
        self.title_font = pygame.font.Font(None, 64)
        self.title = self.title_font.render("Hand Drawing Challenge", True, Colors.TEXT)
        self.title_rect = self.title.get_rect(
            centerx=screen_size[0] // 2,
            top=50
        )
    
    def setup_menu_items(self) -> None:
        """Create and position menu items."""
        # Calculate positions based on screen size
        center_x = self.screen_size[0] // 2
        start_y = self.screen_size[1] // 2
        spacing = 80

        items_data = [
            ("Single Player", lambda: self.start_game_mode("single_player")),
            ("Competitive", lambda: self.start_game_mode("competitive")),
            ("Exit", lambda: (pygame.quit(), exit(0)))
        ]
        
        for i, (text, callback) in enumerate(items_data):
            y_pos = start_y + i * spacing
            self.items.append(MenuItem(text, (center_x, y_pos), callback))
    
    def start_game_mode(self, mode_type: str) -> None:
        """Start a specific game mode.
        
        Args:
            mode_type: Type of game mode to start ("single_player" or "competitive")
        """
        if self.mode_factory:
            self.current_mode = self.mode_factory(mode_type, self.screen_size)
            if self.current_mode:
                self.current_mode.initialize()
                self.current_mode.start_new_game()
                self.transition_to(GameStateType.PLAYING)
    
    def update(self, delta_time: float) -> None:
        """Update menu state.
        
        Args:
            delta_time: Time elapsed since last update
        """
        mouse_pos = pygame.mouse.get_pos()
        for item in self.items:
            item.update(mouse_pos)
    
    def draw(self) -> None:
        """Draw the menu state."""
        # Get the game screen
        screen = pygame.display.get_surface()
        
        # Draw background
        screen.fill(self.background_color)
        
        # Draw title
        screen.blit(self.title, self.title_rect)
        
        # Draw menu items
        for item in self.items:
            item.draw(screen)
    
    def handle_input(self, event: Any) -> None:
        """Handle input events.
        
        Args:
            event: Pygame event to process
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Left click
            for item in self.items:
                if item.is_hovered:
                    item.action()  # Call the callback function
