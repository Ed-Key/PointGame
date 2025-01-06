from typing import Tuple

# Type alias for RGB colors
ColorRGB = Tuple[int, int, int]

class Colors:
    """Color constants for the UI."""
    
    # Basic colors
    BLACK: ColorRGB = (0, 0, 0)
    WHITE: ColorRGB = (255, 255, 255)
    RED: ColorRGB = (255, 0, 0)
    GREEN: ColorRGB = (0, 255, 0)
    BLUE: ColorRGB = (0, 0, 255)
    
    # UI colors
    BACKGROUND: ColorRGB = BLACK
    TEXT: ColorRGB = WHITE
    BORDER: ColorRGB = (128, 128, 128)  # Gray
    
    # Drawing colors
    DRAWING_ACTIVE: ColorRGB = GREEN
    DRAWING_INACTIVE: ColorRGB = RED
    TRAIL_COLOR: ColorRGB = (0, 255, 0)  # Green
    
    # Button colors
    BUTTON_NORMAL: ColorRGB = (128, 128, 128)  # Gray
    BUTTON_HOVER: ColorRGB = (160, 160, 160)  # Light Gray
    BUTTON_PRESSED: ColorRGB = (100, 100, 100)  # Dark Gray