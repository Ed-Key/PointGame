# hand_drawing_challenge/application/config.py
from dataclasses import dataclass
from typing import Tuple

@dataclass
class GameConfig:
    """Global game configuration settings."""
    screen_size: Tuple[int, int] = (1280, 720)
    fps: int = 60
    debug_mode: bool = False
    
    # Input settings
    camera_device: int = 0
    camera_width: int = 640
    camera_height: int = 480
    
    # Game settings
    max_players: int = 4
    round_time: int = 60
    min_accuracy: float = 0.7