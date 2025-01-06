import pygame
from typing import Any, Tuple, Dict, Optional
from ..base import GameState, GameStateType
from ui.utils.colors import Colors

class ResultsState(GameState):
    """Game results state handling."""
    
    def __init__(self, screen_size: Tuple[int, int]):
        """Initialize results state.
        
        Args:
            screen_size: (width, height) of game window
        """
        super().__init__()
        self.screen_size = screen_size
        
        # Font setup
        self.title_font = pygame.font.Font(None, 64)
        self.font = pygame.font.Font(None, 36)
        
        # Button setup
        button_width = 200
        button_height = 50
        self.button_rects: Dict[str, pygame.Rect] = {
            'menu': pygame.Rect(
                (self.screen_size[0] - button_width) // 2,
                self.screen_size[1] - 150,
                button_width,
                button_height
            ),
            'retry': pygame.Rect(
                (self.screen_size[0] - button_width) // 2,
                self.screen_size[1] - 220,
                button_width,
                button_height
            )
        }
        
        self.hovered_button: Optional[str] = None
        self.final_score = 0
        self.accuracy = 0.0
        self.time_bonus = 0
        
        # Achievement tracking
        self.new_achievements: list[str] = []
        self.show_achievements = False
        self.achievement_timer = 0
    
    def set_results(self, score: int, accuracy: float, time_bonus: int, 
                   new_achievements: Optional[list[str]] = None) -> None:
        """Set the final results to display.
        
        Args:
            score: Final score
            accuracy: Drawing accuracy percentage
            time_bonus: Time bonus points
            new_achievements: List of newly unlocked achievements
        """
        self.final_score = score
        self.accuracy = accuracy
        self.time_bonus = time_bonus
        self.new_achievements = new_achievements or []
        self.show_achievements = bool(self.new_achievements)
        self.achievement_timer = 3.0  # Show achievements for 3 seconds
    
    def update(self, delta_time: float) -> None:
        """Update results state.
        
        Args:
            delta_time: Time elapsed since last update
        """
        mouse_pos = pygame.mouse.get_pos()
        
        # Update button hover states
        self.hovered_button = None
        for button_name, button_rect in self.button_rects.items():
            if button_rect.collidepoint(mouse_pos):
                self.hovered_button = button_name
                break
        
        # Update achievement display timer
        if self.show_achievements:
            self.achievement_timer -= delta_time
            if self.achievement_timer <= 0:
                self.show_achievements = False
    
    def draw(self) -> None:
        """Draw the results state."""
        screen = pygame.display.get_surface()
        screen.fill(Colors.BACKGROUND)
        
        # Draw title
        title = self.title_font.render("Results", True, Colors.TEXT)
        title_rect = title.get_rect(
            centerx=self.screen_size[0] // 2,
            top=50
        )
        screen.blit(title, title_rect)
        
        # Draw results
        results_text = [
            f"Final Score: {self.final_score}",
            f"Accuracy: {self.accuracy:.1f}%",
            f"Time Bonus: +{self.time_bonus}"
        ]
        
        y_offset = 200
        for text in results_text:
            surface = self.font.render(text, True, Colors.TEXT)
            rect = surface.get_rect(
                centerx=self.screen_size[0] // 2,
                top=y_offset
            )
            screen.blit(surface, rect)
            y_offset += 50
        
        # Draw achievement notifications if active
        if self.show_achievements:
            self._draw_achievements(screen)
        
        # Draw buttons
        self._draw_buttons(screen)
    
    def _draw_buttons(self, screen: pygame.Surface) -> None:
        """Draw menu buttons.
        
        Args:
            screen: Surface to draw on
        """
        button_text = {
            'menu': 'Main Menu',
            'retry': 'Try Again'
        }
        
        for button_name, rect in self.button_rects.items():
            # Draw button background
            color = Colors.BUTTON_HOVER if button_name == self.hovered_button else Colors.BUTTON_NORMAL
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, Colors.BORDER, rect, 2)
            
            # Draw button text
            text = self.font.render(button_text[button_name], True, Colors.TEXT)
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)
    
    def _draw_achievements(self, screen: pygame.Surface) -> None:
        """Draw achievement notifications.
        
        Args:
            screen: Surface to draw on
        """
        if not self.new_achievements:
            return
            
        # Create semi-transparent overlay
        overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        
        # Draw achievement box
        box_width = 400
        box_height = 100 + (len(self.new_achievements) * 40)
        box_rect = pygame.Rect(
            (self.screen_size[0] - box_width) // 2,
            (self.screen_size[1] - box_height) // 2,
            box_width,
            box_height
        )
        
        pygame.draw.rect(overlay, (50, 50, 50, 230), box_rect)
        pygame.draw.rect(overlay, Colors.BORDER, box_rect, 2)
        
        # Draw achievement title
        title = self.font.render("New Achievements!", True, Colors.TEXT)
        title_rect = title.get_rect(
            centerx=box_rect.centerx,
            top=box_rect.top + 20
        )
        
        # Draw achievements list
        y_offset = title_rect.bottom + 20
        for achievement in self.new_achievements:
            text = self.font.render(f"🏆 {achievement}", True, Colors.TEXT)
            rect = text.get_rect(
                centerx=box_rect.centerx,
                top=y_offset
            )
            overlay.blit(text, rect)
            y_offset += 40
        
        # Draw overlay
        screen.blit(overlay, (0, 0))
    
    def handle_input(self, event: Any) -> None:
        """Handle input events.
        
        Args:
            event: Pygame event to process
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Left click
            if self.hovered_button == 'menu':
                self.transition_to(GameStateType.MENU)
            elif self.hovered_button == 'retry':
                self.transition_to(GameStateType.PLAYING)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Skip achievement display
                self.show_achievements = False
                self.achievement_timer = 0
            elif event.key == pygame.K_ESCAPE:
                self.transition_to(GameStateType.MENU)