# test_harness.py

import pygame
import sys
from game import create_game_mode
from game.base import GameConfig
from game.managers import CompetitiveGameManager
from ui.utils.colors import Colors
from typing import Dict, Optional, List

class GameTestHarness:
    """Test harness to demonstrate and test game functionality."""
    
    def __init__(self, width: int = 1280, height: int = 720):
        """Initialize the test harness.
        
        Args:
            width: Window width in pixels
            height: Window height in pixels
        """
        pygame.init()
        pygame.display.set_caption("Hand Drawing Challenge - Test Harness")
        
        self.screen_size = (width, height)
        self.screen = pygame.display.set_mode(self.screen_size)
        self.clock = pygame.time.Clock()
        
        # Font setup
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)
        
        # Game mode management
        self.current_mode = None
        self.game_config = GameConfig()
        
        # Player management for competitive mode
        self.competitive_manager = CompetitiveGameManager()
        
        # UI State
        self.show_player_dialog = False
        self.player_name_input = ""
        self.show_help = False
        
        # Create UI areas
        self.setup_ui_areas()
        
    def setup_ui_areas(self) -> None:
        """Set up UI button areas and regions."""
        button_height = 50
        button_width = 200
        spacing = 20
        
        # Main menu buttons
        self.buttons: Dict[str, pygame.Rect] = {
            'single_player': pygame.Rect(
                (self.screen_size[0] - button_width) // 2,
                200,
                button_width,
                button_height
            ),
            'competitive': pygame.Rect(
                (self.screen_size[0] - button_width) // 2,
                200 + button_height + spacing,
                button_width,
                button_height
            ),
            'add_player': pygame.Rect(
                (self.screen_size[0] - button_width) // 2,
                200 + (button_height + spacing) * 2,
                button_width,
                button_height
            ),
            'help': pygame.Rect(
                (self.screen_size[0] - button_width) // 2,
                200 + (button_height + spacing) * 3,
                button_width,
                button_height
            )
        }
        
        # Player name input dialog
        dialog_width = 400
        dialog_height = 200
        self.player_dialog_rect = pygame.Rect(
            (self.screen_size[0] - dialog_width) // 2,
            (self.screen_size[1] - dialog_height) // 2,
            dialog_width,
            dialog_height
        )
        
    def draw_button(self, rect: pygame.Rect, text: str, 
                    hovered: bool = False) -> None:
        """Draw a button with hover effect."""
        color = Colors.BUTTON_HOVER if hovered else Colors.BUTTON_NORMAL
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, Colors.BORDER, rect, 2)
        
        text_surface = self.font.render(text, True, Colors.TEXT)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)
        
    def draw_player_dialog(self) -> None:
        """Draw the add player dialog."""
        # Draw semi-transparent overlay
        overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        # Draw dialog box
        pygame.draw.rect(self.screen, Colors.BACKGROUND, self.player_dialog_rect)
        pygame.draw.rect(self.screen, Colors.BORDER, self.player_dialog_rect, 2)
        
        # Draw title
        title = self.font.render("Add New Player", True, Colors.TEXT)
        title_rect = title.get_rect(
            centerx=self.player_dialog_rect.centerx,
            top=self.player_dialog_rect.top + 20
        )
        self.screen.blit(title, title_rect)
        
        # Draw input field
        input_rect = pygame.Rect(
            self.player_dialog_rect.left + 20,
            self.player_dialog_rect.centery - 20,
            self.player_dialog_rect.width - 40,
            40
        )
        pygame.draw.rect(self.screen, Colors.BUTTON_NORMAL, input_rect)
        pygame.draw.rect(self.screen, Colors.BORDER, input_rect, 2)
        
        # Draw input text
        text_surface = self.font.render(self.player_name_input, True, Colors.TEXT)
        text_rect = text_surface.get_rect(
            midleft=(input_rect.left + 10, input_rect.centery)
        )
        self.screen.blit(text_surface, text_rect)
        
    def draw_help(self) -> None:
        """Draw help overlay with controls and information."""
        overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 192))
        self.screen.blit(overlay, (0, 0))
        
        help_text = [
            "Controls:",
            "SPACE - Toggle Drawing",
            "C - Clear Canvas",
            "ESC - Pause Game",
            "Q - Quit to Menu",
            "",
            "Player Management:",
            f"Current Players: {self.competitive_manager.get_player_count()}",
            "Add players before starting competitive mode"
        ]
        
        y_offset = 100
        for line in help_text:
            text = self.font.render(line, True, Colors.TEXT)
            rect = text.get_rect(
                centerx=self.screen_size[0] // 2,
                top=y_offset
            )
            self.screen.blit(text, rect)
            y_offset += 40
            
    def draw_player_list(self) -> None:
        """Draw the current list of players."""
        if self.competitive_manager.get_player_count() == 0:
            return
            
        y_offset = 400
        title = self.font.render("Current Players:", True, Colors.TEXT)
        title_rect = title.get_rect(
            centerx=self.screen_size[0] // 2,
            top=y_offset
        )
        self.screen.blit(title, title_rect)
        
        y_offset += 40
        for player in self.competitive_manager.players.values():
            text = self.font.render(f"• {player.name}", True, Colors.TEXT)
            rect = text.get_rect(
                centerx=self.screen_size[0] // 2,
                top=y_offset
            )
            self.screen.blit(text, rect)
            y_offset += 30
        
    def handle_input(self, event: pygame.event.Event) -> bool:
        """Handle input events.
        
        Returns:
            bool: False if the game should quit, True otherwise
        """
        if event.type == pygame.QUIT:
            return False
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not self.show_player_dialog and not self.show_help:
                mouse_pos = pygame.mouse.get_pos()
                for button_name, button_rect in self.buttons.items():
                    if button_rect.collidepoint(mouse_pos):
                        if button_name == 'single_player':
                            self.start_single_player()
                        elif button_name == 'competitive':
                            self.start_competitive()
                        elif button_name == 'add_player':
                            self.show_player_dialog = True
                        elif button_name == 'help':
                            self.show_help = True
            
        elif event.type == pygame.KEYDOWN:
            if self.show_player_dialog:
                if event.key == pygame.K_RETURN:
                    if self.player_name_input.strip():
                        self.competitive_manager.add_player(self.player_name_input.strip())
                        self.player_name_input = ""
                        self.show_player_dialog = False
                elif event.key == pygame.K_ESCAPE:
                    self.show_player_dialog = False
                    self.player_name_input = ""
                elif event.key == pygame.K_BACKSPACE:
                    self.player_name_input = self.player_name_input[:-1]
                else:
                    if len(self.player_name_input) < 20:  # Max name length
                        self.player_name_input += event.unicode
            elif self.show_help:
                if event.key == pygame.K_ESCAPE:
                    self.show_help = False
            elif self.current_mode:
                self.current_mode.handle_input(event)
                
        return True
        
    def start_single_player(self) -> None:
        """Start single player mode."""
        print("Starting single player mode...")  # Debug print
        try:
            self.current_mode = create_game_mode(
                "single_player",
                self.screen_size,
                self.game_config
            )
            if self.current_mode:
                # print("Game mode created successfully")  # Debug print
                # print("Initializing game mode...")  # Debug print
                # self.current_mode.initialize()
                print("Starting game mode...")  # Debug print
                self.current_mode.start()
                print("Single player mode started successfully")  # Debug print
        except Exception as e:
            print(f"Failed to start single player mode: {e}")
            import traceback
            traceback.print_exc()  # This will print the full error stack
            self.current_mode = None
            
    def start_competitive(self) -> None:
        """Start competitive mode if enough players."""
        if self.competitive_manager.get_player_count() < 2:
            print("Need at least 2 players for competitive mode!")
            return
            
        self.current_mode = create_game_mode(
            "competitive",
            self.screen_size,
            self.game_config
        )
        if self.current_mode:
            self.current_mode.initialize()
            self.current_mode.start()
            
    def run(self) -> None:
        """Main game loop."""
        running = True
        
        while running:
            # Handle events
            for event in pygame.event.get():
                running = self.handle_input(event)
                
            # Clear screen
            self.screen.fill(Colors.BACKGROUND)
            
            if self.current_mode:
                # Update and draw current game mode
                self.current_mode.update(self.clock.get_time() / 1000.0)
                self.current_mode.draw()
            else:
                # Draw menu
                title = self.title_font.render(
                    "Hand Drawing Challenge", True, Colors.TEXT)
                title_rect = title.get_rect(
                    centerx=self.screen_size[0] // 2,
                    top=50
                )
                self.screen.blit(title, title_rect)
                
                # Draw buttons
                mouse_pos = pygame.mouse.get_pos()
                for button_name, button_rect in self.buttons.items():
                    hovered = button_rect.collidepoint(mouse_pos)
                    self.draw_button(
                        button_rect,
                        button_name.replace('_', ' ').title(),
                        hovered
                    )
                
                # Draw player list
                self.draw_player_list()
            
            # Draw overlays
            if self.show_player_dialog:
                self.draw_player_dialog()
            elif self.show_help:
                self.draw_help()
            
            pygame.display.flip()
            self.clock.tick(60)
            
        pygame.quit()

def main():
    """Entry point for the test harness."""
    harness = GameTestHarness()
    harness.run()

if __name__ == "__main__":
    main()