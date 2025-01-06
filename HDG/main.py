# main.py
from ui.game_ui import GameUI

def main():
    """Main entry point for the Hand Drawing Challenge application."""
    try:
        # Create and run game UI
        game = GameUI()
        game.run()
    except Exception as e:
        print(f"Error running application: {e}")
        
if __name__ == "__main__":
    main()