from typing import Optional, Tuple, Dict, Type
from .base import GameMode, GameConfig
from .modes.single_player import SinglePlayerMode
from .modes.competitive import CompetitiveMode

# Map mode types to their implementations
MODE_TYPES: Dict[str, Type[GameMode]] = {
    "single_player": SinglePlayerMode,
    "competitive": CompetitiveMode
}

def create_game_mode(mode_type: str, screen_size: Tuple[int, int], config: Optional[GameConfig] = None) -> Optional[GameMode]:
    """Factory function to create game modes.
    
    Args:
        mode_type: Type of game mode to create ("single_player" or "competitive")
        screen_size: Screen dimensions (width, height)
        config: Optional game configuration
    
    Returns:
        Created game mode instance or None if type is invalid
    """
    print(f"Creating game mode: {mode_type}")  # Debug print
    mode_class = MODE_TYPES.get(mode_type)
    if mode_class:
        print(f"Found mode class: {mode_class.__name__}")  # Debug print
        mode = mode_class(screen_size, config)
        print("Mode instance created, initializing...")  # Debug print
        mode.initialize()  # Make sure we call initialize
        print("Mode initialized successfully")  # Debug print
        return mode
    print(f"No mode class found for type: {mode_type}")  # Debug print
    return None

# Export commonly used types and functions
__all__ = [
    'GameMode',
    'GameConfig',
    'create_game_mode'
]